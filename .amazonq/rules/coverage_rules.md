# Test Coverage Rules

## Include All Endpoint Folders in Coverage Reports

When configuring test coverage for this project, ensure that:

- All endpoint folders are explicitly included in coverage configuration
- The pytest.ini file includes all endpoint directories with `--cov=directory_name`
- The Makefile's test-cov command includes all endpoint directories
- Coverage reports are generated for both terminal and HTML formats

When adding a new endpoint folder to the project:
1. Update pytest.ini to include the new folder in coverage measurement
2. Update the Makefile's test-cov command to include the new folder
3. Verify that coverage reports include the new folder

This rule ensures comprehensive test coverage reporting across all API endpoints and prevents gaps in coverage metrics.