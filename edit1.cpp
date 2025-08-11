#include "edit1.hpp"
#include <algorithm>
#include <cctype>
#include <string>

// ======================= One-edit logic =======================

static Edit1Result equalLengthReplace(const std::string& A, const std::string& B) {
    Edit1Result r;
    int diffIdx = -1;
    for (size_t i = 0; i < A.size(); ++i) {
        if (A[i] != B[i]) {
            if (diffIdx != -1) return r; // more than one difference
            diffIdx = static_cast<int>(i);
        }
    }
    r.withinOne = true;
    r.type = (diffIdx == -1 ? Edit1Type::NONE : Edit1Type::REPLACE);
    r.index = (diffIdx == -1 ? -1 : diffIdx);
    return r;
}

static Edit1Result oneLongerInsertDelete(const std::string& longer, const std::string& shorter, bool longerIsA) {
    Edit1Result r;
    size_t i = 0, j = 0;
    int skipIdx = -1;
    while (i < longer.size() && j < shorter.size()) {
        if (longer[i] == shorter[j]) { ++i; ++j; }
        else {
            if (skipIdx != -1) return r; // already skipped once → >1 edit
            skipIdx = static_cast<int>(i); // skip longer[i]
            ++i;
        }
    }
    if (skipIdx == -1) {
        // difference is at the last char of 'longer'
        skipIdx = static_cast<int>(longer.size() - 1);
    }
    r.withinOne = true;
    r.type = (longerIsA ? Edit1Type::DELETE_ : Edit1Type::INSERT);
    // index where the effect is observed relative to 'shorter'
    r.index = std::min(skipIdx, static_cast<int>(shorter.size()));
    return r;
}

// *** DEFINITION *** (this was missing / mismatched)
Edit1Result withinOneEdit(const std::string& A, const std::string& B) {
    if (A.size() == B.size()) {
        return equalLengthReplace(A, B);
    }
    if (A.size() + 1 == B.size()) {
        return oneLongerInsertDelete(B, A, /*longerIsA=*/false); // INSERT in B (missing in A)
    }
    if (B.size() + 1 == A.size()) {
        return oneLongerInsertDelete(A, B, /*longerIsA=*/true);  // DELETE from A (extra in A)
    }
    return {}; // more than one edit
}

// ======================= Score logic =======================

static std::string sanitizeKeepSpacesNoPunct(const std::string& s) {
    std::string tmp;
    tmp.reserve(s.size());
    for (unsigned char ch : s) {
        if (std::ispunct(ch)) continue;                // להתעלם מסימני פיסוק
        if (std::isalpha(ch)) tmp.push_back((char)std::tolower(ch));
        else if (std::isspace(ch)) tmp.push_back(' '); // לשמור רווחים
        else tmp.push_back((char)std::tolower(ch));    // תווים אחרים – נשמרים (lower)
    }
    // לכווץ רצפי רווחים לרווח יחיד + trim
    std::string out;
    out.reserve(tmp.size());
    bool inSpace = false;
    for (char c : tmp) {
        if (c == ' ') {
            if (!inSpace) { out.push_back(' '); inSpace = true; }
        } else {
            out.push_back(c);
            inSpace = false;
        }
    }
    // trim רווח מוביל/סוגר
    if (!out.empty() && out.front() == ' ') out.erase(out.begin());
    if (!out.empty() && out.back()  == ' ') out.pop_back();
    return out;
}


static int penaltyReplaceAt(int zeroBasedPos) {
    switch (zeroBasedPos) {
        case 0: return 5;
        case 1: return 4;
        case 2: return 3;
        case 3: return 2;
        default: return 1;
    }
}

static int penaltyAddDelAt(int zeroBasedPos) {
    switch (zeroBasedPos) {
        case 0: return 10;
        case 1: return 8;
        case 2: return 6;
        case 3: return 4;
        default: return 2;
    }
}

int computeScore(const std::string& userQuery, const std::string& matchedSegment) {
    std::string q = sanitizeKeepSpacesNoPunct(userQuery);
    std::string m = sanitizeKeepSpacesNoPunct(matchedSegment);

    // קודם היה: int base = 2 * (int)q.size();
    int base = 2 * (int)std::min(q.size(), m.size());  // תואם נספח: "matching letters"

    if (q == m) return base;

    Edit1Result r = withinOneEdit(q, m);
    if (!r.withinOne) return 0;

    int pos = std::max(0, r.index);
    int penalty = 0;

    switch (r.type) {
        case Edit1Type::REPLACE: penalty = penaltyReplaceAt(pos); break;
        case Edit1Type::INSERT:  penalty = penaltyAddDelAt(pos);  break;
        case Edit1Type::DELETE_: penalty = penaltyAddDelAt(pos);  break;
        case Edit1Type::NONE:    return base;
    }
    return base - penalty;
}

