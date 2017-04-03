%module pymitlm

%include <std_string.i>
%include <std_vector.i>

%{
#include "includes.h"
#include "pymitlm.h"
%}

namespace std {
   %template(StringVector) vector<string>;
}

%include "pymitlm.h"
