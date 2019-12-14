local p = { }

p.enemyFighterPowerDataTb = {
    ["1510"] = 8,
    ["1512"] = 10,
    ["1523"] = 24,
    ["1525"] = 27,
    ["1528"] = 28,
    ["1536"] = 27,
    ["1537"] = 27,
    ["1538"] = 27,
    ["1539"] = 38,
    ["1540"] = 38,
    ["1544"] = 44,
    ["1545"] = 48,
    ["1546"] = 35,
    ["1547"] = 41,
    ["1548"] = 47,
    ["1549"] = 29,
    ["1550"] = 29,
    ["1551"] = 29,
    ["1556"] = 98,
    ["1560"] = 23,
    ["1561"] = 94,
    ["1562"] = 107,
    ["1565"] = 102,
    ["1573"] = 80,
    ["1574"] = 159,
    ["1579"] = 84,
    ["1581"] = 76,
    ["1582"] = 109,
    ["1583"] = 110,
    ["1584"] = 91,
    ["1585"] = 96,
    ["1586"] = 106,
    ["1587"] = 76,
    ["1588"] = 109,
    ["1589"] = 72,
    ["1590"] = 105,
    ["1599"] = 111,
    ["1600"] = 111,
    ["1605"] = 94,
    ["1606"] = 103,
    ["1607"] = 103,
    ["1608"] = 114,
    ["1613"] = 53,
    ["1614"] = 100,
    ["1615"] = 103,
    ["1616"] = 108,
    ["1617"] = 126,
    ["1618"] = 132,
    ["1619"] = 117,
    ["1620"] = 129,
    ["1625"] = 22,
    ["1626"] = 72,
    ["1627"] = 88,
    ["1631"] = 206,
    ["1632"] = 206,
    ["1633"] = 216,
    ["1634"] = 150,
    ["1635"] = 160,
    ["1636"] = 207,
    ["1650"] = 34,
    ["1651"] = 48,
    ["1652"] = 68,
    ["1653"] = 34,
    ["1654"] = 48,
    ["1655"] = 68,
    ["1656"] = 48,
    ["1657"] = 68,
    ["1658"] = 88,
    ["1668"] = 59,
    ["1669"] = 82,
    ["1670"] = 9999,
    ["1671"] = 78,
    ["1679"] = 120,
    ["1680"] = 146,
    ["1681"] = 174,
    ["1682"] = 130,
    ["1683"] = 157,
    ["1699"] = 9999,
    ["1700"] = 9999,
    ["1701"] = 96,
    ["1702"] = 54,
    ["1703"] = 74,
    ["1704"] = 9999,
    ["1708"] = 9999,
    ["1709"] = 111,
    ["1710"] = 137,
    ["1711"] = 137,
    ["1712"] = 255,
    ["1713"] = 266,
    ["1714"] = 120,
    ["1715"] = 158,
    ["1716"] = 67,
    ["1717"] = 75,
    ["1718"] = 83,
    ["1719"] = 72,
    ["1720"] = 79,
    ["1721"] = 86,
    ["1722"] = 102,
    ["1723"] = 136,
    ["1724"] = 160,
    ["1725"] = 54,
    ["1726"] = 63,
    ["1727"] = 72,
    ["1728"] = 48,
    ["1729"] = 56,
    ["1730"] = 64,
    ["1731"] = 54,
    ["1732"] = 63,
    ["1733"] = 72,
    ["1734"] = 97,
    ["1735"] = 111,
    ["1745"] = 55,
    ["1746"] = 64,
    ["1747"] = 67,
    ["1748"] = 64,
    ["1749"] = 67,
    ["1750"] = 72,
    ["1751"] = 109,
    ["1752"] = 115,
    ["1753"] = 40,
    ["1754"] = 48,
    ["1755"] = 61,
    ["1756"] = 87,
    ["1757"] = 107,
    ["1758"] = 87,
    ["1759"] = 107,
    ["1760"] = 112,
    ["1761"] = 42,
    ["1762"] = 69,
    ["1763"] = 77,
    ["1764"] = 93,
    ["1765"] = 106,
    ["1766"] = 132,
    ["1767"] = 72,
    ["1768"] = 76,
    ["1769"] = 81,
    ["1770"] = 98,
    ["1771"] = 120,
    ["1772"] = 126,
    ["1776"] = 126,
    ["1777"] = 107,
    ["1778"] = 132,
    ["1779"] = 107,
    ["1780"] = 150,
    ["1781"] = 154,
    ["1782"] = 154,
    ["1783"] = 115,
    ["1784"] = 135,
    ["1785"] = 135,
    ["1786"] = 115,
    ["1787"] = 135,
    ["1788"] = 135,
    ["1799"] = 9999,
    ["1800"] = 183,
    ["1801"] = 183,
    ["1802"] = 225,
    ["1803"] = 225,
    ["1804"] = 225,
    ["1809"] = 40,
    ["1810"] = 45,
    ["1811"] = 48,
    ["1815"] = 66,
    ["1816"] = 72,
    ["1817"] = 82,
    ["1821"] = 105,
    ["1822"] = 119,
    ["1823"] = 132,
    ["1824"] = 119,
    ["1825"] = 132,
    ["1826"] = 142,
    ["1834"] = 64,
    ["1835"] = 67,
    ["1836"] = 72,
    ["1837"] = 67,
    ["1838"] = 72,
    ["1839"] = 78,
    ["1840"] = 50,
    ["1841"] = 60,
    ["1842"] = 80,
    ["1843"] = 60,
    ["1844"] = 70,
    ["1845"] = 90,
    ["1852"] = 62,
    ["1853"] = 88,
    ["1854"] = 107,
    ["1855"] = 62,
    ["1856"] = 88,
    ["1857"] = 107,
    ["1865"] = 35,
    ["1866"] = 41,
    ["1867"] = 47,
    ["1868"] = 44,
    ["1869"] = 50,
    ["1870"] = 54,
    ["1889"] = 71,
    ["1890"] = 105,
    ["1891"] = 140,
    ["1892"] = 9999,
    ["1893"] = 9999,
    ["1894"] = 9999,
    ["1906"] = 148,
    ["1907"] = 186,
    ["1908"] = 197,
}

p.enemyFighterPowerDataTb2 = {

    -- 陆航阶段的深海栖舰制空值
    ["1505"] = 1,
    ["1518"] = 1,
    ["1506"] = 1,
    ["1519"] = 1,
    ["1555"] = 1,
    ["1507"] = 1,
    ["1520"] = 1,
    ["1509"] = 1,
    ["1522"] = 2,
    ["1527"] = 2,
    ["1566"] = 4,
    ["1511"] = 1,
    ["1529"] = 2,
    ["1567"] = 4,
    ["1541"] = 2,
    ["1543"] = 2,
    ["1591"] = 1,
    ["1592"] = 1,
    ["1594"] = 2,
    ["1595"] = 2,
    ["1601"] = 1,
    ["1602"] = 1,
    ["1603"] = 2,
    ["1604"] = 2,
    ["1659"] = 4,
    ["1660"] = 4,
    ["1661"] = 4,
    ["1662"] = 4,
    ["1663"] = 4,
    ["1664"] = 4,
    ["1684"] = 4,
    ["1685"] = 4,
    ["1686"] = 4,
    ["1687"] = 4,
    ["1688"] = 4,
    ["1689"] = 4,
    ["1705"] = 4,
    ["1706"] = 4,
    ["1707"] = 4,
}

return p

