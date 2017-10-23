#!/usr/bin/python
#    Copyright 2013, 2014, 2017 Joshua Charles Campbell
#
#    This file is part of UnnaturalCode.
#    
#    UnnaturalCode is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    UnnaturalCode is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with UnnaturalCode.  If not, see <http://www.gnu.org/licenses/>.

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical
import sys

from tempfile import mkdtemp

from unnaturalcode.validation.test import ValidationTest
from unnaturalcode.validation.file import ValidationFile
from unnaturalcode.validation.tools import tools_by_name
from unnaturalcode.validation.mutators import get_mutation_by_name

class ValidationMain(object):
    
    validation_file_class = ValidationFile
    validation_test_class = ValidationTest
    
    def add_args(self, parser):
        """For overriding in subclasses to add more args."""
        pass 
    
    def read_args(self, args):
        """For overriding in subclasses to add more args."""
        pass
   
    def main(self):
        logging.basicConfig(stream=sys.stderr, level=logging.NOTSET)
        from argparse import ArgumentParser
        parser = ArgumentParser(description="Test and Valide UnnaturalCode")
        parser.add_argument('-t', '--mutation-file-list', nargs='?', 
                            help='List of files to Test')
        parser.add_argument('-T', '--train-file-list', nargs='?', 
                            help='List of files to train on.'
                                ' Default same as test.')
        parser.add_argument('-k', '--keep-corpus', action='store_true', 
                            help="Don't reset the corpus")
        parser.add_argument('-n', '--iterations', type=int, 
                            help='Number of times to iterate', default=50)
        parser.add_argument('-N', '--n-training-files', type=int, 
                            help='Number of training files to use', default=1e64)
        parser.add_argument('-o', '--output-dir', 
                            help='Location to store output files', default='.')
        parser.add_argument('-m', '--mutation', 
                            help='Mutation to use', 
                            required=True, action='append')
        parser.add_argument('-r', '--retry-valid', action='store_true', 
                            help='Retry until a syntactically incorrect'
                            ' mutation is found')
        parser.add_argument('-p', '--pair-file-list', nargs='?',
                            help='File containing list of files in the format'
                                ' after.java which have a matching before.java')
        parser.add_argument('-P', '--pair-file-limit', type=int,
                            help='Limit the number of pair files to '
                            'this number of good files.',
                            default=1e64)
        parser.add_argument('-x', '--tool', 
                            help='Tool to use (example: mitlm)', 
                            required=True, action='append')
        parser.add_argument('-I', '--discard-identifiers', action='store_true',
                            help='Models are only allowed to see token types'
                            'such as <IDENTIFIER> rather than myClass.')
        self.add_args(parser) # get more args from subclasses
        
        args=parser.parse_args()

        test_extra_options = self.read_args(args) # let subclasses read their args
        
        DEBUG(self.validation_file_class)
        
        output_dir = ((args.output_dir 
                                or os.getenv("ucResultsDir", None)) 
                            or mkdtemp(prefix='ucValidation-'))
        
        tools = tools_by_name(args.tool, 
                                language_file=self.validation_file_class,
                                train=args.train_file_list,
                                keep=args.keep_corpus,
                                results_dir=output_dir,
                                type_only=args.discard_identifiers,
                                N=args.n_training_files,
                            )
        
        test = self.validation_test_class(
            language_file=self.validation_file_class,
            output_dir=output_dir,
            type_only=args.discard_identifiers,
            **test_extra_options
        )
        
        if args.mutation_file_list:
            mutations = [
                get_mutation_by_name(mutation) for mutation in args.mutation
            ]
            test.add_mutation_tests(
                test=args.mutation_file_list,
                retry_valid=args.retry_valid,
                mutations=mutations,
                n=args.iterations,
                tools=tools,
                )
        
        if args.pair_file_list:
            test.add_pair_tests(
                test=args.pair_file_list,
                limit=args.pair_file_limit,
                tools=tools,
            )
        ERROR(type(test))
        test.resume()
        ERROR(type(test))
        test.go()
            
