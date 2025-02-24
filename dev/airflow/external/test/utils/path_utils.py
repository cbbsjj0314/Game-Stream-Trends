from datetime import datetime, timezone


def generate_storage_path(data_layer, data_origin, data_category, storage_type="data"):
    """
    데이터를 저장할 기본 경로(디렉토리)를 생성하는 함수.

    Args:
        data_layer (str): 데이터 계층 (예: "bronze", "silver", "gold")
        data_origin (str): 데이터 출처 (예: "steam")
        data_category (str): 데이터 카테고리 (예: "details", "players")
        storage_type (str): "data" 또는 "logs" (기본값: "data")

    Returns:
        str: 생성된 디렉토리 경로 (파일명 제외)
    """
    now = datetime.now(timezone.utc)
    return (
        f"{storage_type}/{data_layer}/{data_origin}/{data_category}/"
        f"year={now.year}/month={now.month:02d}/day={now.day:02d}/hour={now.hour:02d}/"
    )


# 테스트
# dir_path = generate_storage_path("bronze", "steam", "players", storage_type="data")
# print("디렉토리 경로:", dir_path)

# file_name = f"players_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}.json"
# full_path = dir_path + file_name
# print("최종 저장 경로:", full_path)
