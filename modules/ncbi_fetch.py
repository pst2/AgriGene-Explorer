import io
import time
import urllib.error
from typing import List, Tuple

import pandas as pd
import streamlit as st
from Bio import Entrez, SeqIO


class NCBIFetcher:
    """Lớp hỗ trợ tương tác với NCBI Entrez API theo cách an toàn hơn."""

    MAX_RETRIES = 3

    @staticmethod
    def _apply_rate_limit() -> None:
        """
        Giới hạn tốc độ gọi API.
        Dùng chậm hơn một chút để giảm khả năng bị NCBI chặn.
        """
        delay = 0.3 if st.session_state.get("ncbi_api_key") else 1.0
        time.sleep(delay)

    @staticmethod
    def _setup_entrez() -> None:
        """
        Thiết lập thông tin xác thực cho Entrez.
        """
        email = st.session_state.get("ncbi_email")
        if not email:
            raise ValueError("Vui lòng thiết lập Email trong trang 'Cài đặt' trước khi tìm kiếm.")

        Entrez.email = email
        Entrez.tool = "AgriGeneExplorer"

        api_key = st.session_state.get("ncbi_api_key")
        if api_key:
            Entrez.api_key = api_key

    @staticmethod
    def _is_html_response(raw: str) -> bool:
        """
        Kiểm tra response có phải HTML hay không.
        """
        raw_lower = raw.lower()
        return "<html" in raw_lower or "<!doctype html" in raw_lower

    @staticmethod
    def _is_blocked_response(raw: str) -> bool:
        """
        Kiểm tra NCBI có đang trả trang chặn/diagnostic hay không.
        """
        raw_lower = raw.lower()
        return "blocked diagnostic" in raw_lower or "www error blocked diagnostic" in raw_lower

    @staticmethod
    def _decode_response(raw) -> str:
        """
        Chuyển response về string an toàn.
        """
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)

    @staticmethod
    def _build_search_term(query: str, organism: str, gene_type: str) -> str:
        """
        Tạo search term cho NCBI Entrez.
        """
        term_parts = []

        if query and query.strip():
            term_parts.append(f"({query.strip()}[Gene])")

        if organism and organism.strip():
            term_parts.append(f"({organism.strip()}[Organism])")

        if gene_type and gene_type != "All":
            term_parts.append(f"({gene_type}[Feature key])")

        return " AND ".join(term_parts)

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def search_sequences(
        query: str,
        organism: str,
        gene_type: str,
        max_results: int = 50,
    ) -> List[str]:
        """
        Tìm kiếm sequence trên NCBI Nucleotide database.

        Returns:
            Danh sách NCBI IDs.
        """
        NCBIFetcher._setup_entrez()

        search_term = NCBIFetcher._build_search_term(query, organism, gene_type)
        if not search_term:
            st.error("Vui lòng nhập ít nhất từ khóa gen hoặc tên loài.")
            return []

        last_error = None

        for attempt in range(NCBIFetcher.MAX_RETRIES):
            try:
                NCBIFetcher._apply_rate_limit()

                handle = Entrez.esearch(
                    db="nucleotide",
                    term=search_term,
                    retmax=max_results,
                    retmode="xml",
                )
                raw = handle.read()
                handle.close()

                raw_text = NCBIFetcher._decode_response(raw).strip()

                if not raw_text:
                    last_error = "NCBI không trả về dữ liệu."
                    time.sleep(1.5 * (attempt + 1))
                    continue

                if NCBIFetcher._is_html_response(raw_text):
                    if NCBIFetcher._is_blocked_response(raw_text):
                        last_error = (
                            "NCBI đang chặn request tạm thời. "
                            "Hãy đợi một lúc, giảm tần suất gọi API, hoặc đổi mạng."
                        )
                        time.sleep(2.5 * (attempt + 1))
                        continue

                    st.error("NCBI trả về HTML thay vì XML. Có thể máy chủ đang lỗi hoặc response không hợp lệ.")
                    with st.expander("Xem phản hồi từ NCBI"):
                        st.code(raw_text[:2000])
                    return []

                record = Entrez.read(io.StringIO(raw_text))
                return list(record.get("IdList", []))

            except urllib.error.HTTPError as e:
                last_error = f"Lỗi HTTP từ NCBI: {e.code}"
                time.sleep(2.0 * (attempt + 1))
            except urllib.error.URLError as e:
                last_error = f"Lỗi kết nối mạng: {e.reason}"
                time.sleep(2.0 * (attempt + 1))
            except Exception as e:
                last_error = f"Lỗi không xác định khi tìm kiếm: {str(e)}"
                time.sleep(2.0 * (attempt + 1))

        if last_error:
            st.error(last_error)
        return []

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_records(id_list: List[str], rettype: str = "gb") -> pd.DataFrame:
        """
        Tải metadata từ danh sách ID NCBI và chuyển thành DataFrame.
        """
        if not id_list:
            return pd.DataFrame()

        NCBIFetcher._setup_entrez()
        data = []
        last_error = None

        for attempt in range(NCBIFetcher.MAX_RETRIES):
            try:
                NCBIFetcher._apply_rate_limit()

                handle = Entrez.efetch(
                    db="nucleotide",
                    id=",".join(id_list),
                    rettype=rettype,
                    retmode="text",
                )
                records = SeqIO.parse(handle, rettype)

                for rec in records:
                    organism = rec.annotations.get("organism", "Unknown")
                    date = rec.annotations.get("date", "Unknown")

                    gene_type = "Genomic"
                    for feature in rec.features:
                        if feature.type in ["CDS", "mRNA", "rRNA", "tRNA"]:
                            gene_type = feature.type
                            break

                    data.append(
                        {
                            "Accession": rec.id,
                            "Organism": organism,
                            "Description": rec.description,
                            "Length": len(rec.seq),
                            "Gene Type": gene_type,
                            "Submission Date": date,
                        }
                    )

                handle.close()
                return pd.DataFrame(data)

            except urllib.error.HTTPError as e:
                last_error = f"Lỗi HTTP khi tải metadata: {e.code}"
                time.sleep(2.0 * (attempt + 1))
            except urllib.error.URLError as e:
                last_error = f"Lỗi kết nối mạng khi tải records: {e.reason}"
                time.sleep(2.0 * (attempt + 1))
            except Exception as e:
                last_error = f"Lỗi khi tải metadata: {str(e)}"
                time.sleep(2.0 * (attempt + 1))

        if last_error:
            st.error(last_error)
        return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_fasta(accession_id: str) -> Tuple[str, str]:
        """
        Tải FASTA theo accession ID.

        Returns:
            (header, sequence). Nếu lỗi thì trả về ("", "").
        """
        NCBIFetcher._setup_entrez()

        if not accession_id or not accession_id.strip():
            st.error("Vui lòng nhập Accession ID hợp lệ.")
            return "", ""

        last_error = None

        for attempt in range(NCBIFetcher.MAX_RETRIES):
            try:
                NCBIFetcher._apply_rate_limit()

                handle = Entrez.efetch(
                    db="nucleotide",
                    id=accession_id.strip(),
                    rettype="fasta",
                    retmode="text",
                )
                record = SeqIO.read(handle, "fasta")
                handle.close()

                return record.description, str(record.seq)

            except urllib.error.HTTPError as e:
                last_error = f"Lỗi HTTP khi tải FASTA: {e.code}"
                time.sleep(2.0 * (attempt + 1))
            except urllib.error.URLError as e:
                last_error = f"Lỗi kết nối mạng khi tải FASTA: {e.reason}"
                time.sleep(2.0 * (attempt + 1))
            except Exception as e:
                last_error = f"Lỗi khi tải FASTA cho {accession_id}: {str(e)}"
                time.sleep(2.0 * (attempt + 1))

        if last_error:
            st.error(last_error)
        return "", ""