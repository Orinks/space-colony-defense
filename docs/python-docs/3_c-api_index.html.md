### Navigation
  * index
  * modules |
  * next |
  * previous |
  * ![Python logo](https://docs.python.org/3/_static/py.svg)
  * Python »
  * EnglishSpanish | españolFrench | françaisItalian | italianoJapanese | 日本語Korean | 한국어Polish | polskiBrazilian Portuguese | Português brasileiroTurkish | TürkçeSimplified Chinese | 简体中文Traditional Chinese | 繁體中文
dev (3.14)3.13.23.123.113.103.93.83.73.63.53.43.33.23.13.02.72.6
  * 3.13.2 Documentation » 
  * Python/C API Reference Manual
  * | 
  * Theme  Auto Light Dark |


# Python/C API Reference Manual¶
This manual documents the API used by C and C++ programmers who want to write extension modules or embed Python. It is a companion to Extending and Embedding the Python Interpreter, which describes the general principles of extension writing but does not document the API functions in detail.
  * Introduction
    * Coding standards
    * Include Files
    * Useful macros
    * Objects, Types and Reference Counts
    * Exceptions
    * Embedding Python
    * Debugging Builds
  * C API Stability
    * Unstable C API
    * Stable Application Binary Interface
    * Platform Considerations
    * Contents of Limited API
  * The Very High Level Layer
  * Reference Counting
  * Exception Handling
    * Printing and clearing
    * Raising exceptions
    * Issuing warnings
    * Querying the error indicator
    * Signal Handling
    * Exception Classes
    * Exception Objects
    * Unicode Exception Objects
    * Recursion Control
    * Standard Exceptions
    * Standard Warning Categories
  * Utilities
    * Operating System Utilities
    * System Functions
    * Process Control
    * Importing Modules
    * Data marshalling support
    * Parsing arguments and building values
    * String conversion and formatting
    * PyHash API
    * Reflection
    * Codec registry and support functions
    * PyTime C API
    * Support for Perf Maps
  * Abstract Objects Layer
    * Object Protocol
    * Call Protocol
    * Number Protocol
    * Sequence Protocol
    * Mapping Protocol
    * Iterator Protocol
    * Buffer Protocol
  * Concrete Objects Layer
    * Fundamental Objects
    * Numeric Objects
    * Sequence Objects
    * Container Objects
    * Function Objects
    * Other Objects
  * Initialization, Finalization, and Threads
    * Before Python Initialization
    * Global configuration variables
    * Initializing and finalizing the interpreter
    * Process-wide parameters
    * Thread State and the Global Interpreter Lock
    * Sub-interpreter support
    * Asynchronous Notifications
    * Profiling and Tracing
    * Reference tracing
    * Advanced Debugger Support
    * Thread Local Storage Support
    * Synchronization Primitives
  * Python Initialization Configuration
    * Example
    * PyWideStringList
    * PyStatus
    * PyPreConfig
    * Preinitialize Python with PyPreConfig
    * PyConfig
    * Initialization with PyConfig
    * Isolated Configuration
    * Python Configuration
    * Python Path Configuration
    * Py_GetArgcArgv()
    * Multi-Phase Initialization Private Provisional API
  * Memory Management
    * Overview
    * Allocator Domains
    * Raw Memory Interface
    * Memory Interface
    * Object allocators
    * Default Memory Allocators
    * Customize Memory Allocators
    * Debug hooks on the Python memory allocators
    * The pymalloc allocator
    * The mimalloc allocator
    * tracemalloc C API
    * Examples
  * Object Implementation Support
    * Allocating Objects on the Heap
    * Common Object Structures
    * Type Objects
    * Supporting Cyclic Garbage Collection
  * API and ABI Versioning
  * Monitoring C API
  * Generating Execution Events
    * Managing the Monitoring State


#### Previous topic
1. Embedding Python in Another Application
#### Next topic
Introduction
### This Page
  * Report a Bug
  * Show Source 


«
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * ![Python logo](https://docs.python.org/3/_static/py.svg)
  * Python »
  * EnglishSpanish | españolFrench | françaisItalian | italianoJapanese | 日本語Korean | 한국어Polish | polskiBrazilian Portuguese | Português brasileiroTurkish | TürkçeSimplified Chinese | 简体中文Traditional Chinese | 繁體中文
dev (3.14)3.13.23.123.113.103.93.83.73.63.53.43.33.23.13.02.72.6
  * 3.13.2 Documentation » 
  * Python/C API Reference Manual
  * | 
  * Theme  Auto Light Dark |


©  Copyright  2001-2025, Python Software Foundation. This page is licensed under the Python Software Foundation License Version 2. Examples, recipes, and other code in the documentation are additionally licensed under the Zero Clause BSD License. See History and License for more information. The Python Software Foundation is a non-profit corporation. Please donate. Last updated on Feb 22, 2025 (18:18 UTC). Found a bug? Created using Sphinx 8.2.1. 
