#!/usr/bin/python
#    Copyright 2017 Joshua Charles Campbell
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

class Tool(object):
    def __init__(self,
                 language_file,
                 results_dir,
                 N,
                 train=None,
                 keep=None,
                 type_only=False,
                 ):
        self.language_file=language_file
        self.language=language_file.language
        self.results_dir = results_dir
        self.type_only = type_only
        self.N=N
    
    def train_files(self, train):
        pass
    
    def query(self, bad_text):
        raise NotImplementedError()

class Tools(object):
    def mitlm(**kwargs):
        from unnaturalcode.validation.tools.mitlm import Mitlm
        return Mitlm(**kwargs)

    def sensibility(**kwargs):
        from unnaturalcode.validation.tools.sensibility import Sensibility
        return Sensibility(**kwargs)

    def dualmitlm(**kwargs):
        from unnaturalcode.validation.tools.mitlm import DualMitlm
        return DualMitlm(**kwargs)


def tools_by_name(names, **kwargs):
    tools = [getattr(Tools, name.lower()) for name in names]
    tools = [tool(**kwargs) for tool in tools]
    return tools
