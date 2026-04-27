"""OpenAI function tool 스키마 정의.
Assistant가 이 함수들을 호출하면 executor.py가 처리한다.
"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "키워드로 관련 문서를 검색합니다. "
                "Local 파일, exemDocs, Google Drive, ClickUp에서 통합 검색합니다. "
                "사용자가 특정 문서나 데이터를 참조해야 할 때 호출하세요."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 키워드 또는 문장",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_webhook",
            "description": (
                "설정된 외부 API webhook을 호출하여 실시간 데이터를 가져옵니다. "
                "성능 지표, 장애 현황 등 동적 데이터가 필요할 때 사용합니다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "호출할 엔드포인트 이름 (예: performance, alert, deploy)",
                    },
                    "params": {
                        "type": "object",
                        "description": "엔드포인트에 전달할 추가 파라미터",
                    },
                },
                "required": ["endpoint"],
            },
        },
    },
]
