#ifndef __MEM_RUBY_STRUCTURES_LRUADDRLIST_HH__
#define __MEM_RUBY_STRUCTURES_LRUADDRLIST_HH__
#include <list>
#include <unordered_map>
#include <inttypes.h>

#include "mem/ruby/common/Address.hh"

// source https://www.geeksforgeeks.org/lru-cache-implementation/

class LRUAddrList {
    // list of addresses
    // fully associative; only 1 set; change here if you want set assoc
    std::list<Addr> m_list;
  
    // store references of key in cache 
    std::unordered_map<Addr, std::list<Addr>::iterator> m_map; 
    uint64_t m_size; // maximum capacity of cache 

  public:

    // default constructor
    LRUAddrList() {
      m_size = 10240;
    }

    // size parameter to constructor
    LRUAddrList(uint64_t size) {
        m_size = size;
    }

    // searches for element in list
    // if present sets MRU and returns true
    // if not present returns false
    bool lookup(Addr addr) {
      if (m_map.find(addr) == m_map.end()) {
        // not present
        return false;
      }
      else {
        // present at m_map[addr]
        // update reference
        m_list.erase(m_map[addr]);
        m_list.push_front(addr);
        m_map[addr] = m_list.begin();
        return true;
      }

      bool ret;
      // not present 
      if (m_map.find(addr) == m_map.end()) {
          ret = false;

          // cache is full
          if (m_list.size() == m_size) {
              // delete least recently used element
              uint64_t last = m_list.back();
    
              // Pops the last element
              m_list.pop_back();
    
              // Erase the last
              m_map.erase(last);
          }
      }
    
      // present
      else {
          ret = true;
          m_list.erase(m_map[addr]);
      }

      // update reference
      m_list.push_front(addr);
      m_map[addr] = m_list.begin();

      return ret;
    }

    void insert(Addr addr) {
      // should not be present
      // assert(m_map.find(addr) == m_map.end());
      
      // list is full
      if (m_list.size() == m_size) {
          // delete least recently used element
          Addr last = m_list.back();

          // Pops the last element
          m_list.pop_back();

          // Erase the last
          m_map.erase(last);
      }

      m_list.push_front(addr);
      m_map[addr] = m_list.begin();
    }

    // to remove an element
    void remove(Addr addr) {
      m_list.erase(m_map[addr]);
      m_map.erase(addr);
    }

};

#endif // __MEM_RUBY_STRUCTURES_LRUADDRLIST_HH__