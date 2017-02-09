.PHONY=all,quality,test,help

all: quality test ## Run static analyzers and tests

clean:
	-rm -rf node_modules/

test: test-py ## Run tests

test-py: deps-test ## Run Python tests
	nosetests video_xblock --with-coverage --cover-package=video_xblock

quality: tools quality-py quality-js ## Run static code analyzers

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pylint -f colorized video_xblock

quality-js:
	eslint video_xblock/static/js/

deps: ## Install project dependencies
	pip install -r requirements.txt
	bower install

deps-test: ## Install dependencies required to run tests
	pip install -r test_requirements.txt

tools: ## Install development tools
	npm install "eslint@^2.12.0" eslint-config-edx "eslint-plugin-dollar-sign@0.0.5" "eslint-plugin-import@^1.9.2"

package:
	echo "Here be static dependencies packaging"

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
