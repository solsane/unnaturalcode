using namespace std;

class PyMitlm {
public:
  PyMitlm(string corpus, int order, string smoothing, bool unk) 
  {
    Logger::SetVerbosity(3);
    _order = order;
    _smoothing = smoothing;
    _unk = unk;
    Logger::Log(1, "[LL] Loading eval set %s...\n", corpus.c_str()); // [i].c_str());
    Logger::Log(1, "[LL] Smoothing %s...\n", smoothing.c_str()); // [i].c_str());
    _lm = new NgramLM(order);
    _lm->Initialize(NULL, unk, 
                corpus.c_str(), NULL, 
                smoothing.c_str(), NULL);
    _params = new ParamVector(_lm->defParams());
    _eval = new LiveGuess(*_lm, (order < 4 ? order : 4));
    Logger::Log(1, "Parameters:\n");
    _lm->Estimate(*_params);
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
      PerplexityOptimizer* perpEval = new PerplexityOptimizer(*_lm, _order);
      Logger::Log(1, "%f %f %f\n", (*_params)[0], (*_params)[1], (*_params)[2]);

      Logger::Log(2, "Input:%s\n", data);
      Zords.push_back(data);
      FakeZFile* zfile = new FakeZFile(Zords);      

// #if NO_SHORT_COMPUTE_ENTROPY
//       perpEval.LoadCorpus(*zfile);
//       p = perpEval.ComputeEntropy(_params);
// #else
        p = perpEval->ShortCorpusComputeEntropy(*zfile, *_params);
// #endif
//       Logger::Log(2, "Live Entropy %lf\n", p);
//       return p;
      return p;
  }
//   double predict(string data) {
//   }
private:
  int _order;
  string _smoothing;
  bool _unk;
  NgramLM * _lm;
  ParamVector * _params;
  LiveGuess * _eval;
};