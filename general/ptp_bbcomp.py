import os
import requests
import json
import argparse

PTPIMG_API_KEY = "PTPIMG_API_KEY" # <-- your ptpimg api key here

def upload_image(image_path, timeout=30):
    payload = {
        'format': 'json',
        'api_key': PTPIMG_API_KEY
    }
    headers = {'referer': 'https://ptpimg.me/index.php'}

    with open(image_path, 'rb') as file:
        files = [('file-upload[0]', file)]  # required field name for ptpimg
        print(f"Uploading image {image_path}")
        try:
            response = requests.post(
                "https://ptpimg.me/upload.php",
                headers=headers,
                data=payload,
                files=files,
                timeout=timeout
            )
            response.raise_for_status()  # raises exception on HTTP error
            response_data = response.json()

            if not response_data or not isinstance(response_data, list) or 'code' not in response_data[0]:
                return {'status': 'failed', 'reason': "Invalid JSON response from ptpimg"}

            code = response_data[0]['code']
            ext = response_data[0]['ext']
            img_url = f"https://ptpimg.me/{code}.{ext}"
            return f"https://ptpimg.me/{code}.{ext}"

        except requests.exceptions.Timeout:
            return {'status': 'failed', 'reason': 'Request timed out'}
        except requests.exceptions.RequestException as e:
            return {'status': 'failed', 'reason': f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {'status': 'failed', 'reason': 'Invalid JSON response from ptpimg'}


# process a directory with subfolders containing images
def upload_directory(base_dir, output_file, folders):
    # collect image lists from each folder
    folder_images = []
    for folder in folders:
        images = [
            os.path.join(folder, f)
            for f in os.listdir(folder)   # trust existing order
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
        ]
        folder_images.append(images)

    # find number of images among folders
    max_len = max(len(imgs) for imgs in folder_images)    
    with open(output_file, "a", encoding="utf-8") as out:
        # interleave uploads
        for i in range(max_len):
            for folder_idx, images in enumerate(folder_images):
                if i < len(images):
                    for attempt in range(2):
                        url = upload_image(images[i])
                        # check for success
                        if url and not (isinstance(url, dict) and url.get('status') == 'failed'):
                            # successful upload
                            out.write(url + "\n")
                            break  # exit retry loop
                        reason = url.get('reason') if isinstance(url, dict) else "Unknown error"
                        # if first attempt failed, print a warning and retry
                        if attempt == 0:
                            print(f"Upload failed for {images[i]}: {reason}, retrying...")
                        else:
                            # second failure → exit
                            print(f"Upload failed again for {images[i]}: {reason}")
                            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload images in subfolders to ptpimg")
    parser.add_argument("directory", help="Base directory containing folders of images")
    parser.add_argument("-o", "--output", help="Output .txt file", default="comparison_bbcode.txt")

    args = parser.parse_args()
    
    folder_names = [f for f in sorted(os.listdir(args.directory)) if os.path.isdir(os.path.join(args.directory, f))]
    folders = [os.path.join(args.directory, f) for f in folder_names]
    
    # write opening comparison tag
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(f"[comparison={','.join(folder_names)}]\n")
    
    # upload images
    upload_directory(args.directory, args.output, folders)
    
    # write closing comparison tag
    with open(args.output, "a", encoding="utf-8") as out:
        out.write("[/comparison]")
    print(f"Upload complete. Results saved to {args.output}")
