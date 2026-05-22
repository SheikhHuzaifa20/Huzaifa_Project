import os
import shutil
from datetime import datetime
from django.conf import settings

class HDFSSimulator:
    """
    Simulates HDFS storage logic by partitioning files into a year/month/day structure.
    """
    BASE_PATH = os.path.join(settings.BASE_DIR, 'hdfs_simulation', 'data')

    @classmethod
    def store_file(cls, uploaded_file, dataset_name):
        now = datetime.now()
        partition_path = os.path.join(
            cls.BASE_PATH,
            f"year={now.year}",
            f"month={now.strftime('%m')}",
            f"day={now.strftime('%d')}"
        )
        
        # Ensure path exists
        os.makedirs(partition_path, exist_ok=True)
        
        # Create a unique filename
        filename = f"{dataset_name}_{now.strftime('%H%M%S')}_{uploaded_file.name}"
        full_path = os.path.join(partition_path, filename)
        
        # Save file
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Return relative path for storage in DB
        return os.path.relpath(full_path, settings.BASE_DIR)

    @classmethod
    def list_files(cls):
        files_list = []
        if not os.path.exists(cls.BASE_PATH):
            return files_list
            
        for root, dirs, files in os.walk(cls.BASE_PATH):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), cls.BASE_PATH)
                files_list.append({
                    'name': file,
                    'path': rel_path,
                    'size': os.path.getsize(os.path.join(root, file))
                })
        return files_list
