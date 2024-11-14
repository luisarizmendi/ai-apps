from huggingface_hub import snapshot_download
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model")
parser.add_argument("-t", "--token")
parser.add_argument("-o", "--output", default="../../../models")
args = parser.parse_args()

snapshot_download(repo_id=args.model,
                  token=args.token,
                  local_dir=f"{args.output}/{args.model.lower()}",
                  local_dir_use_symlinks=True,
                  cache_dir=f"{args.output}/cache")