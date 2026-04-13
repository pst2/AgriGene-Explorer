from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
from typing import List, Dict, Tuple, Any
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
from typing import Tuple

def calculate_gc_content(sequence: str) -> float:
    """
    Tính % GC content của trình tự.
    
    Args:
        sequence (str): Trình tự nucleotide.
        
    Returns:
        float: Tỷ lệ % GC (0-100).
    """
    if not sequence:
        return 0.0
    return gc_fraction(sequence) * 100

def find_orfs(sequence: str, min_length: int = 100) -> List[Tuple[int, int, int]]:
    """
    Tìm Open Reading Frames (ORFs) trên sợi thuận (forward strand).
    
    Args:
        sequence (str): Trình tự nucleotide.
        min_length (int): Chiều dài tối thiểu của ORF (tính bằng nucleotide).
        
    Returns:
        List[Tuple[int, int, int]]: Danh sách các tuple chứa (start_pos, end_pos, frame_index).
    """
    seq_obj = Seq(sequence).upper()
    orfs = []
    
    # Quét qua 3 khung đọc (reading frames 0, 1, 2)
    for frame in range(3):
        # Dịch mã trên khung hiện tại. Dùng '*' làm ký tự stop codon.
        trans = str(seq_obj[frame:].translate(to_stop=False))
        trans_len = len(trans)
        
        start_aa_pos = -1
        for i in range(trans_len):
            if trans[i] == 'M' and start_aa_pos == -1:
                start_aa_pos = i  # Bắt đầu tại codon mã hóa Methionine
            elif trans[i] == '*' and start_aa_pos != -1:
                # Gặp stop codon
                orf_length = (i - start_aa_pos) * 3
                if orf_length >= min_length:
                    start_nt = frame + start_aa_pos * 3
                    end_nt = start_nt + orf_length + 3 # Bao gồm cả stop codon
                    orfs.append((start_nt, end_nt, frame + 1))
                start_aa_pos = -1 # Reset để tìm ORF tiếp theo
                
    return sorted(orfs, key=lambda x: x[0])

def get_basic_stats(sequence: str) -> Dict[str, Any]:
    """
    Lấy các thống kê cơ bản của chuỗi nucleotide.
    
    Args:
        sequence (str): Chuỗi DNA.
        
    Returns:
        Dict[str, Any]: Dictionary chứa thống kê chi tiết.
    """
    seq = sequence.upper()
    length = len(seq)
    
    if length == 0:
        return {}

    a_count = seq.count('A')
    t_count = seq.count('T')
    g_count = seq.count('G')
    c_count = seq.count('C')
    
    at_count = a_count + t_count
    gc_count = g_count + c_count
    
    return {
        "Độ dài (bp)": length,
        "%A": (a_count / length) * 100,
        "%T": (t_count / length) * 100,
        "%G": (g_count / length) * 100,
        "%C": (c_count / length) * 100,
        "GC Content (%)": calculate_gc_content(seq),
        "AT/GC Ratio": (at_count / gc_count) if gc_count > 0 else float('inf'),
        "Codon ATG": seq.count('ATG')
    }

def translate_sequence(sequence: str) -> str:
    """
    Dịch trình tự DNA sang chuỗi protein.
    
    Args:
        sequence (str): Trình tự DNA.
        
    Returns:
        str: Chuỗi axit amin.
    """
    try:
        # Nếu độ dài không chia hết cho 3, cắt bỏ phần thừa để tránh warning
        seq_obj = Seq(sequence)
        remainder = len(seq_obj) % 3
        if remainder != 0:
            seq_obj = seq_obj[:-remainder]
        return str(seq_obj.translate())
    except Exception as e:
        return f"Lỗi dịch mã: {str(e)}"