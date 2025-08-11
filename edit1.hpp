#pragma once
#include <string>

enum class Edit1Type { NONE, REPLACE, INSERT, DELETE_ };

struct Edit1Result {
    bool withinOne = false;
    Edit1Type type = Edit1Type::NONE;
    int index = -1; // 0-based; -1 when NONE
};

// One-edit check (declaration)
Edit1Result withinOneEdit(const std::string& A, const std::string& B);

// Score computation per the appendix
int computeScore(const std::string& userQuery, const std::string& matchedSegment);
