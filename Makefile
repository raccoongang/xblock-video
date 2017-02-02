.PHONY=all,quality,test

all: quality test

test: test-py

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

quality: quality-py quality-js

quality-py:
	pylint video_xblock
	pep8 .

quality-js:
	eslint video_xblock/static/js/

package:
	echo "Here be static dependencies packaging"
