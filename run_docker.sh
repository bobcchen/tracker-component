LOCAL_DIR=/home/user/dev/aipipeline/cv-usecase/pipeline-manager/data

docker run -d --rm \
  --shm-size=2g \
  --ipc=shareable \
  --name=pipeline-manager \
  -v $LOCAL_DIR:/data \
	cv-pipeline-manager:v1 \
	python server.py --servers detector tracker

docker run -d --rm \
	--gpus all \
  --ipc=container:pipeline-manager \
	detector-component:v1 \
	python server.py --service detector --next_service tracker

docker run -it \
	--gpus all \
  --ipc=container:pipeline-manager \
	tracker-component:v1 \
	python server.py --service tracker --record_tracks --save_chips
