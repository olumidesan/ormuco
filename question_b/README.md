
### Solution to Question B ###

Question: The goal of this question is to write a software library that accepts 2 version string as input and
          returns whether one is greater than, equal, or less than the other. As an example: “1.2” is greater 
          than “1.1”. Please provide all test cases you could think of.


directory: `ormuco/question_b/`

#### Testing ####
- The question asked to create a library, so I created one that can be installed with `pip install <library_name>`
  However, I didn't upload to PyPi. Just a local wheel file for testing. Uploading to PyPi felt excessive.

- Install the library using, `pip3 install ./version_string/dist/version_string-0.0.1-py3-none-any.whl`
- Run the test using, `python3 tests.py`

#### Source code Location ####
The actual source code of the library can be found in `./version_string/build/lib/vstring` or `./version_string/vstring`
