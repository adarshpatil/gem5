#include "mem/ruby/common/AddrSet.hh"

#include <iostream>
#include <set>

std::ostream& operator<<(std::ostream& os, const AddrSet& myset) {
    for (const auto& it: myset) {
        os << " " << it;
    }
    return os;
}
