# -*- coding: utf-8 -*-
# Advanced Printing Support
# Copyright: wizzwizz4
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html
#
# Using code from Simple Printing Support
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Exports the cards in the current deck to a HTML file, so they can be
# printed. Card styling is not yet included. Cards are printed in sort field
# order.

import re
from aqt.qt import *
from aqt.utils import openLink
from aqt import mw
from anki.utils import ids2str
from aqt.utils import mungeQA

config = mw.addonManager.getConfig(__name__)

def sortFieldOrderCids(did):
    dids = [did]
    for name, id in mw.col.decks.children(did):
        dids.append(id)
    return mw.col.db.list("""
select c.id from cards c, notes n where did in %s
and c.nid = n.id order by n.sfld""" % ids2str(dids))

def onPrint():
    path = os.path.join(QStandardPaths.writableLocation(
        QStandardPaths.DesktopLocation), "print.html")
    ids = sortFieldOrderCids(mw.col.decks.selected())
    def esc(s):
        # strip off the repeated question in answer if exists
        #s = re.sub("(?si)^.*<hr id=answer>\n*", "", s)
        # remove type answer
        s = re.sub("\[\[type:[^]]+\]\]", "", s)
        return s
    buf = open(path, "w", encoding="utf8")
    buf.write("<html><head>"
              '<meta charset="utf-8">')
    buf.write(mw.baseHTML())
    buf.write("""<style>
img {
  max-width: 100%;
}
body {
  display: flex;
  flex-flow: row wrap;
}
body > div {
  page-break-after: auto;
  border: 1px solid #ccc;
  padding: 1em;
  flex-grow: 1;
  flex-basis: """ + str(config["card_width"]) + """;
  flex-shrink: """ + str(config["flexbox_shrink"]) + """;
}
</style></head><body>""")
    mw.progress.start(immediate=True)
    for j, cid in enumerate(ids):
        c = mw.col.getCard(cid)
        qatxt = c._getQA(True, False)['a']
        qatxt = mungeQA(mw.col, qatxt)
        cont = u'<div>{}</div>'.format(esc(qatxt))
        buf.write(cont)
        if j % 50 == 0:
            mw.progress.update("Cards exported: %d" % (j+1))
    buf.write("</body></html>")
    mw.progress.finish()
    buf.close()
    openLink(QUrl.fromLocalFile(path))

q = QAction(mw)
q.setText("Print")
q.setShortcut(QKeySequence("Ctrl+Alt+P"))
mw.form.menuTools.addAction(q)
q.triggered.connect(onPrint)
