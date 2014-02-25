from setuptools import setup
import multiprocessing
import glob

setup(name='rratelimit',
      version='0.0.3',
      description='Rate limiting classes for redis and redis-py',
      url='http://github.com/HeyImAlex/rratelimit',
      author='Alex Guerra',
      author_email='alex@heyimalex.com',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
      ],
      license='MIT',
      packages=['rratelimit'],
      zip_safe=False,
      test_suite = 'nose.collector',
      tests_require = ['nose>=1.0', 'redis'],
      data_files = [('rratelimit/lua/', glob.glob('rratelimit/lua/*.lua'))]
    )