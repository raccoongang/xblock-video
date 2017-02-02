.PHONY=all,quality,test

all: quality test

test: test-py

test-py:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

quality: quality-py quality-js quality-pep8

quality-py:
	pylint video_xblock

quality-js:
	eslint video_xblock/static/js/

quality-pep8:
	pep8 .

package:
	echo "Here be static dependencies packaging"
