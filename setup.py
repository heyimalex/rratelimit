from setuptools import setup
import multiprocessing

setup(name='rratelimit',
      version='0.0.2',
      description='Rate limiting classes for redis and redis-py',
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
      test_suite = 'nose.collector',
      tests_require = ['nose>=1.0', 'redis']
    )