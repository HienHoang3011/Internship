from langchain_core.tools import tool
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv(override = True)

@tool
def web_search(query: str) -> str:
    """Sử dụng công cụ này để tìm kiếm thông tin trên internet thông qua Tavily API. 
    Đặc biệt hữu ích và CẦN THIẾT trong các trường hợp sau:
    1. Khi cần tìm kiếm ý kiến, quan điểm hoặc lời khuyên từ các CHUYÊN GIA về một vấn đề mà người dùng đang gặp phải.
    2. Khi bạn không chắc chắn về kiến thức của mình và cần tra cứu, xác thực lại thông tin để đảm bảo câu trả lời đưa ra là chính xác và an toàn.
    3. Khi cần tham khảo các phương pháp, tài liệu chuyên ngành, hoặc ý kiến từ chuyên gia tâm lý học để hỗ trợ xử lý và giải quyết các VẤN ĐỀ TÂM LÝ của người dùng một cách chuyên nghiệp và thấu cảm nhất.
    
    Args:
        query (str): Câu truy vấn tìm kiếm (ví dụ: "cách vượt qua trầm cảm theo chuyên gia tâm lý", "phương pháp CBT là gì").
        
    Returns:
        str: Chuỗi văn bản chứa Tiêu đề (Title), Đường dẫn (URL), và Nội dung (Content) của các kết quả tìm kiếm.
    """
    try:
        tavily_client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
        response = tavily_client.search(
            query = query,
            search_depth = "basic",
            max_results = 3
        )
        search_text = ""
        for hit in response["results"]:
            search_text += f"Title: {hit['title']}\n"
            search_text += f"URL: {hit['url']}\n"
            search_text += f"Content: {hit['content']}\n\n"
        
        return search_text
    except Exception as e:
        return f"Error searching web : {str(e)}"