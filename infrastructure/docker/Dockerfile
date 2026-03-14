FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    python3-pip \
    && add-apt-repository -y ppa:openfoam/openfoam \
    && apt-get update \
    && apt-get install -y openfoam \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY run_simulation.sh /workspace/
RUN chmod +x run_simulation.sh

CMD ["./run_simulation.sh"]
