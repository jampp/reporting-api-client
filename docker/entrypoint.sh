#!/bin/sh
###############################################################################

run_tests() {
  pytest tests
}

###############################################################################

case "${1}" in

  '')
    run_tests
  ;;

  run_tests)
    run_tests
  ;;

  docs)
    make docs
  ;;

  host_docs)
    make docs
    cd docs/_build/html
    python -m http.server $DOCS_PORT
  ;;

  *)
    exec "${@}"
  ;;

esac
