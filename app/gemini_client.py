import google.generativeai as genai
from typing import Optional, List
import os

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.client = genai.Client()

    def list_file_stores(self):
        """모든 FileStore 목록 조회"""
        try:
            file_stores = self.client.list_files()
            return list(file_stores)
        except Exception as e:
            print(f"Error listing file stores: {e}")
            return []

    def create_file_store(self, name: str):
        """새 FileStore 생성"""
        try:
            # Gemini API의 File Search는 자동으로 store를 관리하므로
            # 기본 설정으로 파일 업로드 시 자동 처리됨
            return {"success": True, "message": f"File store '{name}' ready for upload"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_file(self, file_path: str, mime_type: str = "application/pdf"):
        """파일 업로드"""
        try:
            with open(file_path, 'rb') as f:
                file = genai.upload_file(
                    file=f,
                    mime_type=mime_type,
                    display_name=os.path.basename(file_path)
                )
            return {
                "success": True,
                "file_id": file.name,
                "file_name": file.display_name,
                "size": file.size_bytes,
                "mime_type": file.mime_type,
                "created_time": str(file.create_time)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files_in_store(self):
        """업로드된 파일 목록 조회"""
        try:
            files = genai.list_files()
            file_list = []
            for file in files:
                file_list.append({
                    "file_id": file.name,
                    "file_name": file.display_name,
                    "size": getattr(file, 'size_bytes', 0),
                    "mime_type": getattr(file, 'mime_type', 'unknown'),
                    "created_time": str(getattr(file, 'create_time', 'unknown'))
                })
            return file_list
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def delete_file(self, file_id: str):
        """파일 삭제"""
        try:
            genai.delete_file(name=file_id)
            return {"success": True, "message": f"File {file_id} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_with_chat(self, query: str, file_ids: List[str]) -> Optional[str]:
        """업로드된 파일에서 Chat으로 검색"""
        try:
            # 파일들을 File Search 도구로 사용하여 질문
            model = genai.GenerativeModel("gemini-2.0-flash")

            # 파일 객체 생성
            files = []
            for file_id in file_ids:
                # file_id는 "files/xxxxx" 형식
                files.append(genai.types.File(name=file_id))

            # File Search를 사용한 생성
            response = model.generate_content(
                [
                    query,
                    *files
                ]
            )

            return response.text
        except Exception as e:
            print(f"Error in search with chat: {e}")
            return f"Error: {str(e)}"

    def get_file_info(self, file_id: str):
        """파일 정보 조회"""
        try:
            file = genai.get_file(name=file_id)
            return {
                "file_id": file.name,
                "file_name": file.display_name,
                "size": getattr(file, 'size_bytes', 0),
                "mime_type": getattr(file, 'mime_type', 'unknown'),
                "created_time": str(getattr(file, 'create_time', 'unknown')),
                "state": getattr(file, 'state', 'unknown')
            }
        except Exception as e:
            return {"error": str(e)}
