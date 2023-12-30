all: run

project_name=example1
openfga_version=latest

run:
	python example1/example1.py

run-openfga:
	docker pull docker.io/openfga/openfga:${openfga_version} && \
		docker run -p 8080:8080 docker.io/openfga/openfga:${openfga_version} run
