#DDI
DDI is a simple client to allow quick interaction with the SolidServer IPAM.

## RPM Release Procedure
1. Bump __version__ in ddi/__init__.py
2. run flit build
3. Copy or link dist/ddi-\<version\>.tar.gz to rpmbuild/sources
4. Bump the changelog in ddi.spec 
5. Copy or link ddi.spec to rpmbuild/specs
6. in rpmbuild/ run rpmbuild -bs specs/ddi.spec
7. Use you favorite tool like mock to build the rpm on the platform.