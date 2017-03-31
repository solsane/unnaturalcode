using namespace std;

class PyMitlm {
public:
  PyMitlm(string corpus, int order, string smoothing, bool unk) 
     : _eval(_lm, (order < 4 ? order : 4)),
     _params(_lm.defParams())
  {
    Logger::SetVerbosity(1);
    _order = order;
    _smoothing = smoothing;
    _unk = unk;
    Logger::Log(1, "[LL] Loading eval set %s...\n", corpus.c_str()); // [i].c_str());
    Logger::Log(1, "[LL] Smoothing %s...\n", smoothing.c_str()); // [i].c_str());
    _lm = NgramLM(order);
    _lm.Initialize(NULL, unk, 
                corpus.c_str(), NULL, 
                smoothing.c_str(), NULL);
    _params = ParamVector(_lm.defParams());
    Logger::Log(1, "Parameters:\n");
    _lm.Estimate(_params);
  }
  virtual ~PyMitlm() {
  }
  int order() {
    return _order;
  }
  string smoothing() {
    return _smoothing;
  }
  bool unk() {
    return _unk;
  }
  double xentropy(string datas) {
      const char * data = datas.c_str();
      double p = 70.0;
      vector<const char *> Zords;
      PerplexityOptimizer perpEval(_lm, _order);

      Zords.push_back(data);
      FakeZFile *zfile = new FakeZFile(Zords);
      Logger::Log(2, "Input:%s\n", data);

// #if NO_SHORT_COMPUTE_ENTROPY
//       perpEval.LoadCorpus(*zfile);
//       p = perpEval.ComputeEntropy(_params);
// #else
       p = perpEval.ShortCorpusComputeEntropy(*zfile, _params);
// #endif
//       Logger::Log(2, "Live Entropy %lf\n", p);
//       return p;
      delete zfile;
      return p;
  }
  string predict(string data) {
      Logger::Log(2, "Live Guess Input: %s\n", data.c_str());

      /* Fun fact! The prediction arugment is ignored, so I'm passing an arbitrary
      * magic constant! */
      std::auto_ptr<std::vector<LiveGuessResult> > results =
        _eval.Predict(data.c_str(), 10);

      int n = results->size();
      Logger::Log(2, "Number of prediction results: %d\n", n);
      Logger::Log(2, "Live Guess Rankings\n");

      /* Concatenate all results to this buffer. */
      std::stringstream output;

      /* Output all predictions, woo! */
      for (int i = 0; i < n; i++) {
        Logger::Log(2, "Starting rank %d\n", i);
        LiveGuessResult res = (*results)[i];
        Logger::Log(2, "\t%f\t%s\n", res.probability, res.str);
        output << res.probability << '\t' << res.str << '\n';

        delete[] res.str;
        res.str = NULL;
      }

      std::string output_str = output.str();

      Logger::Log(2, "Live Guess Rankings Done\n");
      return output_str;
  }
private:
  int _order;
  string _smoothing;
  bool _unk;
  NgramLM _lm;
  ParamVector _params;
  LiveGuess _eval;
};