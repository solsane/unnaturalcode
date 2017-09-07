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

class Result(object):
    @classmethod
    def column_names(cls):
        return [i % (cls.db_name)
                for i in ["%s_rank",
                "%s_start_line",
                "%s_start_col",
                "%s_end_line",
                "%s_end_col",
                "%s_top_distance_lines",
                "%s_top_distance_toks"
                ]
            ]

class LineLocation(Result):
    db_name = "line_location"
    
class WindowLocation(Result):
    db_name = "window_location"

class ExactLocation(Result):
    db_name = "exact_location"
    
class ValidFix(Result):
    db_name = "valid_fix"
    
class TrueFix(Result):
    db_name = "true_fix"
    
        
