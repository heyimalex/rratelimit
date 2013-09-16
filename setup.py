from setuptools import setup

setup(name='rratelimit',
      version='0.0.1',
      description='Rate limiting classes for redis',
      url='http://github.com/HeyImAlex/rratelimit',
      author='Alex Guerra',
      author_email='alex@heyimalex.com',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      license='MIT',
      packages=['rratelimit'],
      zip_safe=False,
      test_suite = "tests.suite")