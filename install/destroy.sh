#!/usr/bin/env bash
rm -rf /opt/jumpscale
rm -rf /JS8/opt/jumpscale
rm -rf /JS8/optvar/
rm -rf /optvar/cfg/
rm -rf /optvar/cfg/markdowndocs/
rm -rf /optvar/markdowndocs_internal/
rm -rf /optvar/log/
rm -rf /optvar/portal/
rm -rf /optvar/capnp/
rm -rf /optvar/build/

set -ex

rm -rf $CODEDIR/github/threefoldtech/jumpscale_ays_jumpscale/
rm -rf $CODEDIR/github/threefoldtech/jumpscale_jumpscale_core/
rm -rf $CODEDIR/github/threefoldtech/jumpscale_jumpscale_portal8/
