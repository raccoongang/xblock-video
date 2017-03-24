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
			 videojs-wistia/src/vjs.wistia.js\
			 videojs-youtube/dist/Youtube.min.js

vendor_css := video.js/dist/video-js.min.css

all: quality test

clean:
	-rm -rf node_modules/

test: test-py test-js

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

test-js:
	karma start video_xblock/static/video_xblock_karma.conf.js

quality: quality-py quality-js

quality-py:
	pep8 . --format=pylint --max-line-length=120
	pylint -f colorized video_xblock
	pydocstyle -e

quality-js:
	eslint video_xblock/static/js/

dev-install:
	# Install package using pip to leverage pip's cache and shorten CI build time
	pip install --process-dependency-links -e .

deps-test:
	pip install -r test_requirements.txt

bower: tools
	bower install

tools:
	npm install

coverage:
	bash <(curl -s https://codecov.io/bash)

$(vendor_js): bower
	cp $(bower_dir)/$@ $(vendor_dir)/js/$(@F)

$(vendor_css): bower
	cp $(bower_dir)/$@ $(vendor_dir)/css/$(@F)

package: $(vendor_js) $(vendor_css)
	@echo "Packaging vendor files..."
