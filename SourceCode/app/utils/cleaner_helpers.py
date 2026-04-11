import re
def remove_table_pattern(text):
    # Define a regex pattern to match tables in markdown
    table_pattern = r'\|(?:[^\n]*\|)+\n(?:\|(?:[^\n]*\|)+\n?)+'

    # Use re.sub to remove all occurrences of the table pattern
    cleaned_text = re.sub(table_pattern, '', text)

    return cleaned_text
def clean_text(text):
    text = remove_table_pattern(text)
    PATTERNS_TO_REMOVE = [
        r"!\[img-\d+\.jpeg\]\(img-\d+\.jpeg\)",  # Xóa link ảnh markdown: ![img-1.jpeg](img-1.jpeg)
        r"^##\s*(?:Trang|Page)?\s+\d+\s*(?:/\s*\d+)?\s*$",  # Xóa dòng số trang: ## Page 52, ## 52 / 100
        r"^\d+(?:\.\d+)*\s+.+?\s+\.{3,}\s+\d+$",  # Xóa dòng mục lục: 1.2.3. Title ..... 56
        r"^\|.+",  # Xóa các dòng bắt đầu bằng |, thường là bảng markdown
    ]
    COMBINED_PATTERNS = re.compile("|".join(PATTERNS_TO_REMOVE), re.MULTILINE | re.IGNORECASE)

    # Pattern để dọn dẹp các dòng trống thừa
    NEWLINE_CLEANUP_PATTERN = re.compile(r'\n{3,}')

    cleaned_text = COMBINED_PATTERNS.sub('', text)
    cleaned_text = NEWLINE_CLEANUP_PATTERN.sub('\n\n', cleaned_text)
    return cleaned_text.strip()