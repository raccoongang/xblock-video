# XBlock SDK Workbench compatible mixin and scenarios

## To run VideoXBlock workbench scenarios

1. Install xblock-sdk in parent directory:
   ```bash
   git clone https://github.com/edx/xblock-sdk/releases/tag/v0.1.3 ../xblock-sdk
   ```
2. Make sure VideoXBlock is installed into your environment:
   ```bash
   make dev-install
   ```

3. Run Workbench:
   ```bash
   ../xblock-sdk/manage.py runserver
   ```
