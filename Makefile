all: quality

test:
	nosetests video_xblock --with-coverage --cover-package=video_xblock

quality:
	pylint video_xblock
	eslint video_xblock/static/js/

package:
	echo "Here be static dependencies packaging"
