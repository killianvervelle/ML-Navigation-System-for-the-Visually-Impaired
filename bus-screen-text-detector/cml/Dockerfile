FROM iterativeai/cml:latest-gpu
RUN sed -i '208 i --docker-ipcmode host \\' /usr/lib/node_modules/@dvcorg/cml/src/drivers/gitlab.js
CMD ["sh", "-c", "cml runner launch --driver gitlab --repo https://gitlab.forge.hefr.ch/pi_aimarket-visionaid/bus-screen-text-detector --token $GITLAB_TOKEN --labels cml-gpu --idle-timeout=-1"]
