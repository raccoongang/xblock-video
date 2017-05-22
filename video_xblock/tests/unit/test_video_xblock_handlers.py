import json
from mock import patch, Mock

from video_xblock import VideoXBlock
from video_xblock.tests.unit.base import VideoXBlockTestBase


class AuthenticateApiHandlerTests(VideoXBlockTestBase):

    @patch.object(VideoXBlock, 'authenticate_video_api')
    def test_auth_video_api_handler_delegates_call(self, auth_video_api_mock):
        # Arrange
        request_mock = Mock()
        request_mock.method = 'POST'
        request_mock.body = '"test-token-123"'  # JSON string
        auth_video_api_mock.return_value = {}, ''

        # Act
        result_response = self.xblock.authenticate_video_api_handler(request_mock)
        result = result_response.body

        # Assert
        self.assertEqual(
            result,
            json.dumps({'success_message': 'Successfully authenticated to the video platform.'})
        )
        auth_video_api_mock.assert_called_once_with('test-token-123')  # Python string
