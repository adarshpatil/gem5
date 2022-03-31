#include <ostream>
#include <set>
#include <inttypes.h>

typedef std::set<uint64_t> AddrSet;
std::ostream& operator<<(std::ostream& os, const std::set<uint64_t>& myset);