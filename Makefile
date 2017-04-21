PATH  := node_modules/.bin:$(PATH)
SHELL := /bin/bash
.PHONY=all,quality,test

bower_dir := bower_components
vendor_dir := video_xblock/static/vendor
vendor_js := video.js/dist/video.min.js\
			 videojs-contextmenu-ui/dist/videojs-contextmenu-ui.min.js\
			 videojs-contextmenu/dist/videojs-contextmenu.min.js\
			 videojs-offset/dist/videojs-offset.min.js\
			 videojs-transcript/dist/videojs-transcript.min.js\
			 videojs-vimeo/src/Vimeo.js\
			 videojs-wistia/vjs.wistia.js\
			 videojs-youtube/dist/Youtube.min.js

vendor_css := video.js/dist/video-js.min.css
vendor_fonts := video-js/dist/font/VideoJS.eot\
				video-js/dist/font/VideoJS.svg\
				video-js/dist/font/VideoJS.ttf\
				video-js/dist/font/VideoJS.woff

all: quality test

clean: # Clean working directory
	-rm -rf node_modules/
	-rm -rf bower_components/
	-find . -name *.pyc -delete

test: test-py test-js ## Run tests

test-py: ## Run Python tests
	nosetests video_xblock --with-coverage --cover-package=video_xblock

test-js: ## Run JavaScript tests
	karma start video_xblock/static/video_xblock_karma.conf.js

quality: quality-py quality-js ## Run code quality checks

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pylint -f colorized video_xblock
	pydocstyle -e

quality-js:
	eslint video_xblock/static/js/

dev-install:
	# Install package using pip to leverage pip's cache and shorten CI build time
	pip install --process-dependency-links -e .

deps-test: ## Install dependencies required to run tests
	pip install -r test_requirements.txt

deps-js: tools
	bower install

tools: ## Install development tools
	npm install

coverage: ## Send coverage reports to coverage sevice
	bash <(curl -s https://codecov.io/bash)

clear-vendored:
	rm -rf $(vendor_dir)/js/*
	rm -rf $(vendor_dir)/css/*
	mkdir $(vendor_dir)/css/fonts

$(vendor_js): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/js/$(@F)

$(vendor_css): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/css/$(@F)

$(vendor_fonts): clear-vendored deps-js
	cp $(bower_dir)/$@ $(vendor_dir)/css/fonts/$(@F)

vendored: $(vendor_js) $(vendor_css) $(vendor_fonts)  ## Update vendored JS/CSS assets
	@echo "Packaging vendor files..."

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
