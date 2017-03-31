#if !__APPLE__
#define SET_FLOATING_POINT_FLAGS 1
#else
#define SET_FLOATING_POINT_FLAGS 0
#endif

#if SET_FLOATING_POINT_FLAGS
#include <fenv.h>
#endif

#define NDEBUG 1

#include <vector>
#include <string>
#include <cstdlib>
#include <cstdio>
#include <ostream>
#include <iomanip>
#include <sstream>

#include "util/CommandOptions.h"



#include "util/ZFile.h"
#include "util/FakeZFile.h"

#include "util/Logger.h"
#include "Types.h"
#include "NgramLM.h"

#include "Smoothing.h"
#include "PerplexityOptimizer.h"

#include "WordErrorRateOptimizer.h"

#include "CrossFolder.h"
#include "LiveGuess.h"
