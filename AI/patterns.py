patterns = {
    "computation": [
        [{"LOWER": {"IN": ["calculate", "compute", "solve", "evaluate", "simplify", "integrate", "differentiate", "factor", "optimize", "model", "simulate", "quantify", "estimate", "predict", "assess", "measure", "add", "subtract", "figure", "reckon", "gauge", "appraise", "determine", "work out", "ascertain", "cipher", "tally", "total", "sum", "multiply", "divide", "analyze numerically", "process mathematically", "derive", "resolve", "extrapolate", "interpolate", "approximate", "forecast", "project", "calibrate", "scale", "quantize", "numerate", "enumerate", "count", "tabulate", "rate", "value", "judge", "rank", "grade", "score", "test", "inspect", "examine", "check", "verify", "validate"]}}],
        [{"LOWER": "do"}, {"LOWER": "math"}, {"LOWER": "on"}],
        [{"LOWER": "run"}, {"LOWER": "calculation"}],
        [{"LOWER": "perform"}, {"POS": "NOUN"}, {"LOWER": "computation"}],
        [{"LOWER": "figure"}, {"LOWER": "out"}, {"POS": "NOUN"}],
        [{"LOWER": "solve"}, {"LOWER": "for"}],
        [{"LOWER": "compute"}, {"LOWER": "the"}, {"LOWER": "value"}],
        [{"LOWER": "estimate"}, {"LOWER": "the"}, {"LOWER": "amount"}],
        [{"LOWER": "evaluate"}, {"LOWER": "expression"}],
        [{"LOWER": "simplify"}, {"LOWER": "equation"}],
        [{"LOWER": "optimize"}, {"LOWER": "process"}],
        [{"LOWER": "model"}, {"LOWER": "scenario"}],
        [{"LOWER": "quantify"}, {"LOWER": "impact"}],
        [{"LOWER": "predict"}, {"LOWER": "outcome"}]
        # Expanded with more variations from synonyms
    ],
    "web_search": [
        [{"LOWER": {"IN": ["search", "find", "lookup", "google", "bing", "query", "browse", "scrape", "crawl", "fetch", "explore", "hunt", "seek", "probe", "investigate", "examine", "scan", "surf", "navigate", "dig", "sift", "trawl", "mine", "extract", "retrieve", "locate", "discover", "uncover", "spot", "detect", "identify", "pinpoint", "track", "trace", "quest", "pursue", "inquire", "research", "delve", "forage", "scour", "comb", "rummage", "root", "fish", "glean", "harvest", "collect", "gather", "obtain", "secure", "access", "download", "pull", "grab", "snag"]}}, {"LOWER": {"IN": ["web", "internet", "online", "site", "page", "url", "net", "cyberspace", "digital", "virtual", "browser", "engine", "portal", "domain", "link", "resource", "content", "data", "info", "information", "results", "hits", "listings", "sources", "repositories", "archives", "databases", "wiki", "forum", "blog", "article", "news", "feed", "stream", "social media"]}}],
        [{"LOWER": "look"}, {"LOWER": "up"}, {"LOWER": "on"}, {"LOWER": "the"}, {"LOWER": "web"}],
        [{"LOWER": "search"}, {"LOWER": "for"}],
        [{"LOWER": "find"}, {"LOWER": "information"}, {"LOWER": "about"}],
        [{"LOWER": "what"}, {"LOWER": "does"}, {"LOWER": "the"}, {"LOWER": "web"}, {"LOWER": "say"}],
        [{"LOWER": "online"}, {"LOWER": "search"}],
        [{"LOWER": "browse"}, {"LOWER": "site"}],
        [{"LOWER": "scrape"}, {"LOWER": "data"}],
        [{"LOWER": "crawl"}, {"LOWER": "pages"}],
        [{"LOWER": "fetch"}, {"LOWER": "results"}],
        [{"LOWER": "query"}, {"LOWER": "engine"}],
        [{"LOWER": "google"}, {"LOWER": "for"}],
        [{"LOWER": "bing"}, {"LOWER": "search"}]
        # More patterns from expanded synonyms
    ],
    "generation": [
        [{"LOWER": {"IN": ["generate", "create", "produce", "make", "build", "craft", "compose", "design", "invent", "formulate", "construct", "fabricate", "manufacture", "develop", "assemble", "forge", "shape", "form", "originate", "conceive", "devise", "contrive", "engineer", "establish", "initiate", "launch", "spawn", "breed", "hatch", "concoct", "brew", "cook up", "whip up", "put together", "piece together", "synthesize", "compile", "author", "write", "draw up", "draft", "prepare", "organize", "structure", "plan", "map out", "outline", "sketch", "blueprint", "prototype", "model", "simulate", "render", "depict", "illustrate", "visualize", "imagine", "envision", "dream up", "brainstorm", "ideate", "innovate", "pioneer", "trailblaze", "revolutionize"]}}, {"POS": "NOUN"}],
        [{"LOWER": "write"}, {"LOWER": {"IN": ["code", "script", "program", "story", "poem", "essay", "article", "plan", "idea", "content", "report", "document", "novel", "book", "letter", "email", "post", "blog", "tutorial", "guide", "manual", "recipe", "formula", "algorithm", "function", "class", "module", "app", "software", "tool", "system", "framework", "design", "blueprint", "prototype", "model", "simulation", "artwork", "drawing", "painting", "illustration", "graphic", "image", "video", "animation", "music", "song", "melody", "composition", "symphony"]}}],
        [{"LOWER": "come"}, {"LOWER": "up"}, {"LOWER": "with"}],
        [{"LOWER": "generate"}, {"LOWER": "a"}, {"LOWER": "new"}],
        [{"LOWER": "create"}, {"LOWER": "content"}],
        [{"LOWER": "produce"}, {"LOWER": "output"}],
        [{"LOWER": "build"}, {"LOWER": "system"}],
        [{"LOWER": "design"}, {"LOWER": "solution"}],
        [{"LOWER": "invent"}, {"LOWER": "method"}],
        [{"LOWER": "formulate"}, {"LOWER": "strategy"}],
        [{"LOWER": "construct"}, {"LOWER": "framework"}],
        [{"LOWER": "devise"}, {"LOWER": "plan"}],
        [{"LOWER": "concoct"}, {"LOWER": "idea"}],
        [{"LOWER": "fabricate"}, {"LOWER": "prototype"}]
        # Vastly expanded with creative synonyms
    ],
    "summarization": [
        [{"LOWER": {"IN": ["summarize", "tl;dr", "condense", "abridge", "shorten", "recap", "outline", "digest", "synopsis", "brief", "epitomize", "encapsulate", "reprise", "consolidate", "compress", "précis", "abstract", "review", "run down", "sum up", "boil down", "distill", "recapitulate", "wrap up", "highlight", "key points", "main ideas", "cliff notes", "quick overview", "short version", "condensation", "breviary", "compendium", "rundown", "extract", "essence", "summing-up", "epitome", "abbreviation", "reduction", "truncation", "curtailment"]}}],
        [{"LOWER": "give"}, {"LOWER": "me"}, {"LOWER": "a"}, {"LOWER": "summary"}],
        [{"LOWER": "key"}, {"LOWER": "points"}, {"LOWER": "of"}],
        [{"LOWER": "condense"}, {"LOWER": "this"}],
        [{"LOWER": "what"}, {"LOWER": "are"}, {"LOWER": "the"}, {"LOWER": "main"}, {"LOWER": "ideas"}],
        [{"LOWER": "recap"}, {"LOWER": "the"}, {"LOWER": "events"}],
        [{"LOWER": "outline"}, {"LOWER": "the"}, {"LOWER": "steps"}],
        [{"LOWER": "digest"}, {"LOWER": "the"}, {"LOWER": "article"}],
        [{"LOWER": "synopsis"}, {"LOWER": "of"}, {"LOWER": "the"}, {"LOWER": "story"}],
        [{"LOWER": "brief"}, {"LOWER": "me"}, {"LOWER": "on"}]
        # More from summary synonyms
    ],
    "explanation": [
        [{"LOWER": {"IN": ["explain", "what", "why", "how", "describe", "elaborate", "clarify", "define", "illustrate", "break", "down", "expound", "explicate", "delineate", "interpret", "demonstrate", "detail", "disclose", "enlighten", "exposit", "express", "annotate", "simplify", "unfold", "reveal", "tell", "spell out", "make clear", "point out", "lay out", "walk through", "shed light", "demystify", "unravel", "decode", "decipher", "construe", "rationalize", "justify", "account for", "reason", "motivate", "discuss", "narrate", "recount", "portray", "depict", "characterize", "analyze", "examine", "probe", "explore", "investigate"]}}, {"LOWER": {"IN": ["is", "does", "means", "works", "happens", "occurs", "results", "causes", "leads to", "implies", "signifies", "represents", "indicates", "suggests", "entails", "involves", "requires", "demands", "necessitates", "presupposes", "assumes"]}}],
        [{"LOWER": "tell"}, {"LOWER": "me"}, {"LOWER": "about"}],
        [{"LOWER": "what"}, {"LOWER": "is"}],
        [{"LOWER": "why"}, {"LOWER": "does"}],
        [{"LOWER": "how"}, {"LOWER": "to"}],
        [{"LOWER": "explain"}, {"LOWER": "in"}, {"LOWER": "detail"}],
        [{"LOWER": "simplify"}, {"LOWER": "this"}, {"LOWER": "concept"}],
        [{"LOWER": "describe"}, {"LOWER": "the"}, {"LOWER": "process"}],
        [{"LOWER": "elaborate"}, {"LOWER": "on"}],
        [{"LOWER": "clarify"}, {"LOWER": "the"}, {"LOWER": "difference"}],
        [{"LOWER": "define"}, {"LOWER": "term"}],
        [{"LOWER": "illustrate"}, {"LOWER": "with"}, {"LOWER": "example"}],
        [{"LOWER": "break"}, {"LOWER": "down"}, {"LOWER": "steps"}]
        # Enhanced with detailed synonyms
    ],
    "translation": [
        [{"LOWER": {"IN": ["translate", "convert", "interpret", "render", "transliterate", "paraphrase", "rephrase", "reword", "transpose", "metaphrase", "gloss", "decode", "decipher", "change", "adapt", "transform", "turn", "shift", "switch", "recast", "reformulate", "express in", "put into", "make sense in", "explain in", "convey in", "transcribe", "transmute", "alter", "modify", "rewrite", "rescript", "dub", "subtitle", "localize", "internationalize"]}}, {"LOWER": {"IN": ["to", "into", "from"]}}, {"POS": "NOUN"}],
        [{"LOWER": "what"}, {"LOWER": "does"}, {"LOWER": "this"}, {"LOWER": "mean"}, {"LOWER": "in"}],
        [{"LOWER": "translate"}, {"LOWER": "this"}, {"LOWER": "text"}],
        [{"LOWER": "change"}, {"LOWER": "language"}, {"LOWER": "to"}],
        [{"LOWER": "convert"}, {"LOWER": "phrase"}, {"LOWER": "to"}],
        [{"LOWER": "interpret"}, {"LOWER": "sentence"}],
        [{"LOWER": "render"}, {"LOWER": "passage"}]
    ],
    "analysis": [
        [{"LOWER": {"IN": ["analyze", "examine", "assess", "evaluate", "dissect", "review", "investigate", "parse", "critique", "deconstruct", "scrutinize", "inspect", "probe", "study", "appraise", "diagnose", "audit", "survey", "check", "explore", "delve", "research", "sift", "canvass", "consider", "ponder", "weigh", "judge", "rate", "grade", "criticize", "break down", "take apart", "decompose", "resolve", "disaggregate", "question", "interrogate", "test", "trial", "experiment", "validate", "verify", "confirm", "corroborate", "substantiate"]}}],
        [{"LOWER": "break"}, {"LOWER": "down"}],
        [{"LOWER": "what"}, {"LOWER": "do"}, {"LOWER": "you"}, {"LOWER": "think"}],
        [{"LOWER": "analyze"}, {"LOWER": "the"}, {"LOWER": "data"}],
        [{"LOWER": "provide"}, {"LOWER": "insights"}, {"LOWER": "on"}],
        [{"LOWER": "examine"}, {"LOWER": "the"}, {"LOWER": "issue"}],
        [{"LOWER": "assess"}, {"LOWER": "the"}, {"LOWER": "impact"}],
        [{"LOWER": "evaluate"}, {"LOWER": "options"}],
        [{"LOWER": "dissect"}, {"LOWER": "problem"}],
        [{"LOWER": "review"}, {"LOWER": "performance"}]
    ],
    "comparison": [
        [{"LOWER": {"IN": ["compare", "contrast", "versus", "vs", "differentiate", "similarities", "differences", "juxtapose", "balance", "weigh", "match", "measure", "parallel", "analogize", "liken", "relate", "correlate", "oppose", "distinguish", "discriminate", "set against", "pit against", "stack up", "hold up", "benchmark", "rate against", "evaluate side by side", "draw parallels", "highlight differences", "identify commonalities", "analyze disparities", "examine variations", "assess relative", "gauge against", "collate", "confront", "counterpose"]}}],
        [{"LOWER": "what"}, {"LOWER": "is"}, {"LOWER": "better"}, {"LOWER": "between"}],
        [{"LOWER": "compare"}, {"LOWER": "and"}, {"LOWER": "contrast"}],
        [{"LOWER": "differences"}, {"LOWER": "between"}],
        [{"LOWER": "similarities"}, {"LOWER": "to"}],
        [{"LOWER": "versus"}, {"LOWER": "the"}, {"LOWER": "other"}],
        [{"LOWER": "differentiate"}, {"LOWER": "from"}]
    ],
    "recommendation": [
        [{"LOWER": {"IN": ["recommend", "suggest", "advise", "propose", "endorse", "pick", "choose", "nominate", "commend", "prescribe", "urge", "encourage", "counsel", "guide", "direct", "instruct", "advocate", "back", "support", "champion", "plug", "tout", "vouch", "certify", "approve", "sanction", "ratify", "validate", "accredit", "select", "opt for", "go for", "favor", "prefer", "tip", "hint", "allude", "imply", "intimate", "broach", "float", "posit", "put forward", "submit", "offer", "tender", "proffer", "volunteer"]}}],
        [{"LOWER": "what"}, {"LOWER": "should"}, {"LOWER": "i"}],
        [{"LOWER": "best"}, {"LOWER": "option"}, {"LOWER": "for"}],
        [{"LOWER": "suggest"}, {"LOWER": "some"}],
        [{"LOWER": "advise"}, {"LOWER": "on"}],
        [{"LOWER": "propose"}, {"LOWER": "a"}, {"LOWER": "solution"}],
        [{"LOWER": "endorse"}, {"LOWER": "product"}],
        [{"LOWER": "pick"}, {"LOWER": "the"}, {"LOWER": "right"}]
    ],
    "definition": [
        [{"LOWER": {"IN": ["define", "definition", "meaning", "what", "is", "describe", "characterize", "designate", "explain", "expound", "interpret", "specify", "spell out", "mark out", "bound", "delineate", "outline", "trace", "demarcate", "limit", "restrict", "confine", "delimit", "set bounds", "fix", "establish", "determine", "clarify", "elucidate", "make precise", "pin down", "nail down", "lay down", "set forth", "stipulate", "prescribe", "label", "name", "term", "denote", "signify", "connote", "represent", "symbolize"]}}, {"LOWER": "of"}],
        [{"LOWER": "what"}, {"LOWER": "does"}, {"LOWER": {"IN": ["mean", "stand", "for", "signify", "represent", "indicate", "denote", "imply", "connote", "symbolize", "entail", "involve"]}}],
        [{"LOWER": "define"}, {"POS": "NOUN"}],
        [{"LOWER": "meaning"}, {"LOWER": "of"}, {"LOWER": "term"}],
        [{"LOWER": "definition"}, {"LOWER": "please"}]
    ],
    "tutorial": [
        [{"LOWER": {"IN": ["how", "guide", "tutorial", "steps", "instructions", "walkthrough", "manual", "directions", "recipe", "procedure", "method", "process", "approach", "technique", "way", "manner", "mode", "system", "protocol", "regimen", "routine", "formula", "blueprint", "template", "framework", "handbook", "reference", "resource", "lesson", "course", "training", "coaching", "mentoring", "teaching", "demonstration", "example", "illustration", "exemplar", "model", "pattern", "paradigm", "archetype", "prototype", "demo", "trial", "test run", "dry run", "rehearsal", "practice"]}}, {"LOWER": "to"}],
        [{"LOWER": "teach"}, {"LOWER": "me"}, {"LOWER": "how"}],
        [{"LOWER": "step"}, {"LOWER": "by"}, {"LOWER": "step"}],
        [{"LOWER": "instructions"}, {"LOWER": "for"}],
        [{"LOWER": "walkthrough"}, {"LOWER": "the"}, {"LOWER": "process"}],
        [{"LOWER": "guide"}, {"LOWER": "me"}, {"LOWER": "through"}]
    ],
    "code_generation": [
        [{"LOWER": {"IN": ["write", "code", "program", "script", "implement", "develop", "build", "create", "design", "author", "compose", "draft", "construct", "engineer", "formulate", "prototype", "assemble", "compile", "debug", "test", "deploy", "execute", "run", "generate code", "code up", "script out", "program in", "implement function", "write algorithm", "build app", "create software", "design system", "author module", "compose class", "draft method", "construct framework", "engineer solution", "formulate logic", "prototype feature", "assemble components", "compile program", "debug code", "test script", "deploy application"]}}, {"LOWER": {"IN": ["code", "function", "class", "algorithm", "script", "program", "app", "software", "tool", "system", "module", "framework", "logic", "feature", "component", "method", "routine", "procedure", "snippet", "block", "library", "package", "extension", "plugin", "macro", "bot", "agent", "automation", "workflow", "pipeline", "sequence", "operation", "command", "instruction", "statement", "expression", "variable", "data structure", "array", "list", "dictionary", "object", "instance"]}}],
        [{"LOWER": "generate"}, {"LOWER": "python"}, {"LOWER": "code"}],
        [{"LOWER": "how"}, {"LOWER": "to"}, {"LOWER": "code"}],
        [{"LOWER": "implement"}, {"LOWER": "in"}, {"LOWER": "java"}],
        [{"LOWER": "write"}, {"LOWER": "script"}, {"LOWER": "for"}],
        [{"LOWER": "program"}, {"LOWER": "a"}, {"LOWER": "function"}]
    ],
    "math": [
        [{"LOWER": {"IN": ["solve", "equation", "formula", "theorem", "proof", "algebra", "geometry", "calculus", "arithmetic", "trigonometry", "statistics", "probability", "differential", "integral", "linear", "matrix", "vector", "set", "graph theory", "number theory", "combinatorics", "topology", "analysis", "discrete", "continuous", "applied", "pure", "mathematical", "numeric", "symbolic", "computational", "theoretical", "empirical", "stochastic", "deterministic", "fractal", "chaotic", "quantum", "relativistic", "Euclidean", "non-Euclidean", "hyperbolic", "elliptic", "Riemannian", "Lorentzian", "Fourier", "Laplace", "Z-transform", "wavelet", "eigenvalue", "eigenvector", "determinant", "inverse", "transpose", "orthogonal", "symmetric", "skew-symmetric", "hermitian", "unitary"]}}],
        [{"LOWER": "mathematical"}, {"LOWER": "problem"}],
        [{"LOWER": "find"}, {"LOWER": "the"}, {"LOWER": "root"}],
        [{"LOWER": "prove"}, {"LOWER": "theorem"}],
        [{"LOWER": "derive"}, {"LOWER": "formula"}],
        [{"LOWER": "integrate"}, {"LOWER": "function"}],
        [{"LOWER": "differentiate"}, {"LOWER": "equation"}],
        [{"LOWER": "factor"}, {"LOWER": "polynomial"}],
        [{"LOWER": "simplify"}, {"LOWER": "expression"}]
    ],
    "reasoning": [
        [{"LOWER": {"IN": ["reason", "think", "deduce", "infer", "logic", "rationalize", "deliberate", "ponder", "muse", "contemplate", "reflect", "speculate", "hypothesize", "postulate", "conjecture", "surmise", "conclude", "derive", "extrapolate", "induce", "abduce", "generalize", "synthesize", "analyze", "evaluate", "assess", "judge", "appraise", "critique", "dissect", "deconstruct", "ratiocinate", "philosophize", "ideate", "brainstorm", "cogitate", "ruminate", "meditate", "brood", "stew", "chew over", "mull over", "turn over", "weigh", "balance", "consider", "examine", "probe", "investigate", "scrutinize", "question", "interrogate", "debate", "argue", "discuss", "dispute", "rebut", "refute", "validate", "verify", "confirm", "corroborate"]}}],
        [{"LOWER": "step"}, {"LOWER": "by"}, {"LOWER": "step"}, {"LOWER": "reasoning"}],
        [{"LOWER": "why"}, {"LOWER": "is"}, {"LOWER": "this"}],
        [{"LOWER": "deduce"}, {"LOWER": "from"}],
        [{"LOWER": "infer"}, {"LOWER": "the"}, {"LOWER": "conclusion"}],
        [{"LOWER": "logic"}, {"LOWER": "behind"}],
        [{"LOWER": "rationalize"}, {"LOWER": "decision"}]
    ],
    "planning": [
        [{"LOWER": {"IN": ["plan", "strategy", "steps", "roadmap", "outline", "schedule", "agenda", "scheme", "design", "program", "project", "blueprint", "framework", "timetable", "calendar", "itinerary", "list", "checklist", "protocol", "procedure", "methodology", "approach", "tactic", "game plan", "master plan", "action plan", "business plan", "strategic plan", "operational plan", "contingency plan", "backup plan", "timeline", "milestone", "phase", "stage", "sequence", "workflow", "pipeline", "process map", "flowchart", "Gantt chart", "PERT chart", "critical path", "resource allocation", "budgeting", "forecasting", "projection", "prioritization", "organization", "coordination", "arrangement", "preparation", "setup", "orchestration", "choreography"]}}],
        [{"LOWER": "how"}, {"LOWER": "to"}, {"LOWER": "plan"}],
        [{"LOWER": "create"}, {"LOWER": "a"}, {"LOWER": "plan"}],
        [{"LOWER": "strategy"}, {"LOWER": "for"}],
        [{"LOWER": "steps"}, {"LOWER": "to"}, {"LOWER": "achieve"}],
        [{"LOWER": "roadmap"}, {"LOWER": "towards"}],
        [{"LOWER": "outline"}, {"LOWER": "the"}, {"LOWER": "path"}],
        [{"LOWER": "schedule"}, {"LOWER": "tasks"}]
    ],
    "creative": [
        [{"LOWER": {"IN": ["story", "poem", "idea", "brainstorm", "imagine", "fiction", "art", "novel", "tale", "narrative", "verse", "rhyme", "lyric", "epic", "ballad", "ode", "sonnet", "haiku", "limerick", "prose", "script", "play", "drama", "comedy", "tragedy", "fantasy", "sci-fi", "mystery", "romance", "horror", "adventure", "biography", "memoir", "essay", "article", "blog", "post", "drawing", "painting", "sculpture", "design", "illustration", "graphic", "music", "song", "melody", "composition", "symphony", "dance", "choreography", "performance", "theater", "film", "video", "animation", "photography", "craft", "invention", "innovation", "concept", "notion", "thought", "vision", "dream", "fantasy", "hallucination", "illusion", "mirage", "delusion", "conception", "ideation", "inspiration", "muse", "spark", "flash", "eureka", "aha moment", "breakthrough", "revelation", "epiphany"]}}],
        [{"LOWER": "tell"}, {"LOWER": "a"}, {"LOWER": "story"}],
        [{"LOWER": "generate"}, {"LOWER": "creative"}, {"LOWER": "content"}],
        [{"LOWER": "brainstorm"}, {"LOWER": "ideas"}],
        [{"LOWER": "imagine"}, {"LOWER": "scenario"}],
        [{"LOWER": "write"}, {"LOWER": "poem"}],
        [{"LOWER": "create"}, {"LOWER": "art"}],
        [{"LOWER": "invent"}, {"LOWER": "story"}],
        [{"LOWER": "devise"}, {"LOWER": "plot"}],
        [{"LOWER": "concoct"}, {"LOWER": "tale"}],
        [{"LOWER": "fabricate"}, {"LOWER": "narrative"}]
    ],
    "question_answering": [  # Default for general queries
        [{"LOWER": {"IN": ["what", "who", "where", "when", "why", "how", "ask", "inquire", "seek", "discover", "learn", "question", "query", "probe", "interrogate", "investigate", "explore", "delve", "quiz", "poll", "survey", "examine", "inspect", "scrutinize", "wonder", "ponder", "contemplate", "speculate", "hypothesize", "postulate", "conjecture", "surmise", "guess", "estimate", "approximate", "tell me", "inform me", "explain to me", "describe to me", "elaborate on", "detail about", "clarify for me", "shed light on", "break down for me", "walk me through", "guide me on", "teach me about", "educate me on", "enlighten me regarding", "fill me in on", "update me about", "brief me on", "recap for me", "summarize to me"]}}],
        [{"LOWER": "tell"}, {"LOWER": "me"}],
        [{"LOWER": "answer"}, {"LOWER": "this"}, {"LOWER": "question"}],
        [{"LOWER": "what"}, {"LOWER": "happened"}],
        [{"LOWER": "who"}, {"LOWER": "is"}],
        [{"LOWER": "where"}, {"LOWER": "can"}, {"LOWER": "i"}, {"LOWER": "find"}],
        [{"LOWER": "when"}, {"LOWER": "does"}],
        [{"LOWER": "why"}, {"LOWER": "is"}],
        [{"LOWER": "how"}, {"LOWER": "works"}]
    ],
    "fact_check": [
        [{"LOWER": {"IN": ["verify", "check", "fact", "true", "false", "confirm", "validate", "authenticate", "corroborate", "substantiate", "prove", "disprove", "refute", "debunk", "authenticate", "certify", "attest", "witness", "vouch", "endorse", "ratify", "sanction", "affirm", "assert", "declare", "pronounce", "state", "avow", "aver", "swear", "testify", "depose", "cross-check", "double-check", "triple-check", "audit", "inspect", "review", "examine", "scrutinize", "probe", "investigate", "research", "look up", "search for truth", "fact-find", "myth-bust", "reality-check", "truth-test", "accuracy-assess", "validity-verify", "authenticity-confirm"]}}],
        [{"LOWER": "is"}, {"LOWER": "this"}, {"LOWER": "true"}],
        [{"LOWER": "fact"}, {"LOWER": "check"}],
        [{"LOWER": "confirm"}, {"LOWER": "the"}, {"LOWER": "facts"}],
        [{"LOWER": "verify"}, {"LOWER": "statement"}],
        [{"LOWER": "check"}, {"LOWER": "if"}, {"LOWER": "false"}]
    ],
    "data_processing": [
        [{"LOWER": {"IN": ["process", "handle", "manipulate", "clean", "transform", "wrangle", "mung", "scrub", "refine", "prepare", "preprocess", "normalize", "standardize", "filter", "sort", "aggregate", "merge", "join", "split", "pivot", "reshape", "encode", "decode", "parse", "extract", "load", "etl", "ingest", "digest", "convert", "format", "validate", "sanitize", "deduplicate", "impute", "interpolate", "extrapolate", "bin", "bucket", "cluster", "segment", "partition", "index", "query", "retrieve", "fetch", "store", "archive", "backup", "restore", "migrate", "sync", "replicate", "batch", "stream", "pipeline", "workflow", "orchestrate", "automate", "script"]}}, {"LOWER": "data"}],
        [{"LOWER": "analyze"}, {"LOWER": "dataset"}],
        [{"LOWER": "clean"}, {"LOWER": "the"}, {"LOWER": "data"}],
        [{"LOWER": "transform"}, {"LOWER": "format"}],
        [{"LOWER": "handle"}, {"LOWER": "input"}],
        [{"LOWER": "manipulate"}, {"LOWER": "records"}]
    ],
    "visualization": [
        [{"LOWER": {"IN": ["visualize", "plot", "graph", "chart", "draw", "diagram", "map", "sketch", "trace", "delineate", "outline", "represent", "depict", "illustrate", "render", "display", "show", "exhibit", "project", "image", "picture", "figure", "infographic", "heatmap", "scatterplot", "line graph", "bar chart", "pie chart", "histogram", "boxplot", "violin plot", "contour", "surface", "3d model", "animation", "dashboard", "report", "canvas", "blueprint", "schematic", "flowchart", "mindmap", "tree diagram", "network graph", "Gantt", "PERT", "timeline", "calendar view", "kanban", "mosaic", "treemap", "sunburst", "radar chart", "polar plot", "bubble chart", "word cloud", "tag cloud", "venn diagram", "euler diagram", "sankey diagram", "chord diagram"]}}],
        [{"LOWER": "show"}, {"LOWER": "me"}, {"LOWER": "a"}, {"LOWER": "graph"}],
        [{"LOWER": "plot"}, {"LOWER": "the"}, {"LOWER": "data"}],
        [{"LOWER": "chart"}, {"LOWER": "results"}],
        [{"LOWER": "draw"}, {"LOWER": "diagram"}],
        [{"LOWER": "visualize"}, {"LOWER": "trends"}]
    ],
    "simulation": [
        [{"LOWER": {"IN": ["simulate", "model", "run", "scenario", "test", "emulate", "imitate", "replicate", "mimic", "copy", "duplicate", "reproduce", "mock", "pretend", "feign", "affect", "assume", "counterfeit", "sham", "fake", "forge", "fabricate", "prototype", "trial", "experiment", "pilot", "dry run", "rehearse", "practice", "role-play", "enact", "stage", "perform", "dramatize", "virtualize", "hypothesize", "predict", "forecast", "project", "extrapolate", "interpolate", "approximate", "estimate", "guess", "surmise", "conjecture", "postulate", "speculate", "theorize", "conceptualize", "abstract", "idealize", "mathematize", "numericalize", "computationalize"]}}],
        [{"LOWER": "what"}, {"LOWER": "if"}],
        [{"LOWER": "run"}, {"LOWER": "simulation"}],
        [{"LOWER": "model"}, {"LOWER": "behavior"}],
        [{"LOWER": "test"}, {"LOWER": "scenario"}],
        [{"LOWER": "emulate"}, {"LOWER": "environment"}]
    ],
    "optimization": [
        [{"LOWER": {"IN": ["optimize", "improve", "maximize", "minimize", "efficient", "enhance", "upgrade", "boost", "streamline", "refine", "fine-tune", "tweak", "adjust", "calibrate", "hone", "perfect", "polish", "augment", "amplify", "intensify", "strengthen", "fortify", "elevate", "raise", "increase", "escalate", "scale up", "expand", "grow", "develop", "advance", "progress", "evolve", "reform", "revamp", "overhaul", "restructure", "reorganize", "rationalize", "economize", "save", "conserve", "reduce", "cut", "trim", "slash", "downsize", "shrink", "curtail", "limit", "constrain", "optimize efficiency", "maximize output", "minimize cost", "improve performance", "enhance productivity", "boost speed", "streamline process", "refine algorithm", "fine-tune parameters", "adjust settings"]}}],
        [{"LOWER": "best"}, {"LOWER": "way"}, {"LOWER": "to"}],
        [{"LOWER": "improve"}, {"LOWER": "the"}, {"LOWER": "system"}],
        [{"LOWER": "maximize"}, {"LOWER": "value"}],
        [{"LOWER": "minimize"}, {"LOWER": "risk"}],
        [{"LOWER": "efficient"}, {"LOWER": "method"}]
    ],
    "database_search": [
        [{"LOWER": {"IN": ["search", "query", "find", "retrieve", "lookup", "extract", "pull", "fetch", "mine", "dig", "sift", "filter", "sort", "aggregate", "join", "merge", "scan", "index", "browse", "navigate", "explore", "delve", "probe", "investigate", "hunt", "track", "trace", "locate", "pinpoint", "identify", "discover", "uncover", "spot", "detect", "access", "obtain", "secure", "download", "grab", "snag", "collect", "gather", "harvest", "compile", "assemble", "curate", "archive", "backup", "restore", "sync", "replicate", "vector search", "semantic search", "full-text search", "keyword search", "fuzzy search", "proximity search", "boolean query", "SQL query", "NoSQL query", "graph query", "time-series query"]}}, {"LOWER": {"IN": ["database", "knowledge", "data", "vector", "db", "repo", "repository", "archive", "dataset", "corpus", "index", "store", "warehouse", "lake", "base", "knowledge base", "information system", "content management", "search engine", "catalog", "library", "collection", "pool", "bank", "vault", "silo", "hub", "portal", "gateway", "interface", "api", "endpoint", "query interface", "search bar", "lookup table", "fact table", "dimension table", "graph db", "document db", "key-value store", "column store", "relational db", "non-relational db"]}}],
        [{"LOWER": "look"}, {"LOWER": "in"}, {"LOWER": "db"}],
        [{"LOWER": "query"}, {"LOWER": "the"}, {"LOWER": "knowledge"}],
        [{"LOWER": "find"}, {"LOWER": "in"}, {"LOWER": "database"}],
        [{"LOWER": "retrieve"}, {"LOWER": "data"}]
    ],
    # New intents from chatbot NLP searches
    "sentiment_analysis": [
        [{"LOWER": {"IN": ["analyze", "sentiment", "emotion", "tone", "mood", "feeling", "attitude", "opinion", "polarity", "positive", "negative", "neutral", "detect sentiment", "gauge emotion", "assess tone", "evaluate mood", "classify feeling", "score attitude", "mine opinion", "extract polarity"]}}],
        [{"LOWER": "what"}, {"LOWER": "is"}, {"LOWER": "the"}, {"LOWER": "sentiment"}],
        [{"LOWER": "analyze"}, {"LOWER": "tone"}, {"LOWER": "of"}, {"LOWER": "text"}]
    ],
    "entity_recognition": [
        [{"LOWER": {"IN": ["recognize", "extract", "identify", "ner", "named entity", "entity", "person", "organization", "location", "date", "time", "money", "quantity", "detect entities", "parse names", "tag entities", "spot organizations", "find locations", "pull dates", "extract quantities"]}}],
        [{"LOWER": "extract"}, {"LOWER": "entities"}, {"LOWER": "from"}],
        [{"LOWER": "identify"}, {"LOWER": "names"}, {"LOWER": "in"}, {"LOWER": "text"}]
    ],
    "classification": [
        [{"LOWER": {"IN": ["classify", "categorize", "label", "tag", "sort", "group", "bucket", "segment", "cluster", "assign class", "determine type", "identify category", "place in group", "organize by label", "stratify", "partition", "divide", "subdivide", "taxonomize", "hierarchize"]}}],
        [{"LOWER": "classify"}, {"LOWER": "this"}, {"LOWER": "as"}],
        [{"LOWER": "categorize"}, {"LOWER": "the"}, {"LOWER": "data"}]
    ],
    "extraction": [
        [{"LOWER": {"IN": ["extract", "pull", "retrieve", "mine", "harvest", "glean", "scrape", "parse", "distill", "isolate", "separate", "filter out", "draw out", "obtain", "acquire", "collect", "gather", "compile", "accumulate", "aggregate", "summarize from", "abstract from", "derive from", "infer from", "deduce from"]}}],
        [{"LOWER": "extract"}, {"LOWER": "information"}, {"LOWER": "from"}],
        [{"LOWER": "pull"}, {"LOWER": "data"}, {"LOWER": "out"}]
    ],
    # Domain-specific from e-commerce, etc.
    "product_search": [
        [{"LOWER": {"IN": ["search", "find", "lookup", "browse", "shop for", "look for", "recommend products", "suggest items", "show catalog", "list goods", "query inventory", "filter by price", "sort by rating", "compare products"]}}, {"LOWER": {"IN": ["product", "item", "goods", "merchandise", "stock", "inventory", "catalog", "selection", "range", "collection", "assortment"]}}],
        [{"LOWER": "find"}, {"LOWER": "products"}, {"LOWER": "like"}],
        [{"LOWER": "search"}, {"LOWER": "for"}, {"LOWER": "item"}]
    ],
    "order_tracking": [
        [{"LOWER": {"IN": ["track", "check", "status", "update on", "where is", "delivery time", "shipment details", "order progress", "package location", "eta", "arrival estimate"]}}, {"LOWER": {"IN": ["order", "shipment", "package", "delivery", "purchase", "transaction", "invoice", "receipt"]}}],
        [{"LOWER": "track"}, {"LOWER": "my"}, {"LOWER": "order"}],
        [{"LOWER": "status"}, {"LOWER": "of"}, {"LOWER": "shipment"}]
    ],
    "support_query": [
        [{"LOWER": {"IN": ["help", "support", "assist", "troubleshoot", "fix", "resolve", "issue", "problem", "complaint", "query", "inquiry", "ticket", "report bug", "customer service", "tech support", "helpdesk"]}}],
        [{"LOWER": "help"}, {"LOWER": "with"}, {"LOWER": "issue"}],
        [{"LOWER": "troubleshoot"}, {"LOWER": "problem"}]
    ],
    "learning_query": [
        [{"LOWER": {"IN": ["learn", "study", "teach", "explain concept", "tutorial on", "course about", "lesson in", "educate on", "knowledge of", "facts about", "history of", "science behind", "math for", "language lesson"]}}],
        [{"LOWER": "teach"}, {"LOWER": "me"}, {"LOWER": "about"}],
        [{"LOWER": "learn"}, {"LOWER": "how"}, {"LOWER": "to"}]
    ],
    "health_advice": [
        [{"LOWER": {"IN": ["health", "symptom", "diagnosis", "treatment", "advice on", "remedy for", "cure", "prevent", "wellness", "fitness", "diet", "exercise", "mental health", "therapy", "medication", "doctor recommend", "hospital find"]}}],
        [{"LOWER": "what"}, {"LOWER": "to"}, {"LOWER": "do"}, {"LOWER": "for"}, {"LOWER": "symptom"}],
        [{"LOWER": "health"}, {"LOWER": "tips"}, {"LOWER": "for"}]
    ],
    "financial_inquiry": [
        [{"LOWER": {"IN": ["finance", "balance", "account", "transaction", "budget", "investment", "loan", "credit", "debit", "payment", "bill", "tax", "savings", "retirement", "stock", "crypto", "market", "rate", "interest", "mortgage", "insurance"]}}],
        [{"LOWER": "check"}, {"LOWER": "balance"}],
        [{"LOWER": "financial"}, {"LOWER": "advice"}]
    ],
    "game_tip": [
        [{"LOWER": {"IN": ["game", "tip", "cheat", "strategy", "guide", "walkthrough", "hint", "trick", "hack", "level up", "win", "beat", "unlock", "achievement", "boss fight", "puzzle solve", "multiplayer", "solo", "quest", "mission", "campaign"]}}],
        [{"LOWER": "tips"}, {"LOWER": "for"}, {"LOWER": "game"}],
        [{"LOWER": "how"}, {"LOWER": "to"}, {"LOWER": "win"}]
    ]
    # Add more new intents as needed from searches
}
