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
	["1670"] = 116,
	["1671"] = 78,
	["1679"] = 120,
	["1680"] = 146,
	["1681"] = 174,
	["1682"] = 130,
	["1683"] = 157,
	["1699"] = 54,
	["1700"] = 74,
	["1701"] = 96,
	["1702"] = 54,
	["1703"] = 74,
	["1704"] = 96,
	["1708"] = 79,
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
	["1799"] = 183,
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
	["1892"] = 91,
	["1893"] = 156,
	["1894"] = 273,
	["1906"] = 148,
	["1907"] = 186,
	["1908"] = 197,
	["1921"] = 36,
	["1922"] = 47,
	["1923"] = 74,
	["1924"] = 51,
	["1925"] = 66,
	["1926"] = 90,
	["1933"] = 34,
	["1934"] = 40,
	["1935"] = 46,
	["1936"] = 40,
	["1937"] = 46,
	["1938"] = 49,
	["1961"] = 114,
	["1962"] = 117,
	["1963"] = 119,
	["1964"] = 138,
	["1971"] = 93,
	["1972"] = 103,
	["1973"] = 118,
	["1974"] = 103,
	["1975"] = 118,
	["1976"] = 155,
	["1994"] = 32,
	["1995"] = 42,
	["1997"] = 140,
	["2015"] = 16,
	["2016"] = 40,
	["2017"] = 46,
	["2018"] = 49,
	["2023"] = 54,
	["2024"] = 75,
	["2025"] = 96,
	["2026"] = 54,
	["2027"] = 75,
	["2028"] = 96,
	["2041"] = 114,
	["2042"] = 123,
	["2043"] = 135,
	["2044"] = 123,
	["2045"] = 135,
	["2046"] = 150,
	["2047"] = 135,
	["2048"] = 166,
	["2059"] = 93,
	["2060"] = 97,
	["2061"] = 160,
	["2062"] = 157,
	["2069"] = 176,
	["2070"] = 191,
	["2071"] = 191,
	["2072"] = 217,
	["2073"] = 34,
	["2074"] = 46,
	["2077"] = 158,
	["2078"] = 224,
	["2079"] = 289,
	["2084"] = 28,
	["2086"] = 56,
	["2088"] = 72,
	["2091"] = 70,
	["2092"] = 108,
	["2093"] = 136,
	["2094"] = 32,
	["2095"] = 60,
	["2096"] = 76,
	["2101"] = 120,
	["2102"] = 136,
	["2103"] = 149,
	["2104"] = 168,
	["2105"] = 168,
	["2106"] = 194,
	["2107"] = 206,
	["2108"] = 230,
	["2115"] = 180,
	["2116"] = 197,
	["2117"] = 200,
	["2118"] = 205,
	["2119"] = 210,
	["2120"] = 160,
	["2121"] = 167,
	["2122"] = 180,
	["2123"] = 160,
	["2124"] = 180,
	["2125"] = 192,
	["2126"] = 180,
	["2127"] = 200,
	["2128"] = 218,
	["2129"] = 200,
	["2130"] = 218,
	["2131"] = 239,
	["2132"] = 67,
	["2133"] = 71,
	["2134"] = 75,
	["2135"] = 71,
	["2136"] = 75,
	["2137"] = 79,
	["2138"] = 20,
	["2139"] = 42,
	["2140"] = 49,
	["2141"] = 56,
	["2146"] = 133,
	["2147"] = 161,
	["2148"] = 183,
	["2149"] = 171,
	["2150"] = 191,
	["2151"] = 208,
	["2152"] = 39,
	["2153"] = 54,
	["2154"] = 65,
	["2155"] = 54,
	["2156"] = 60,
	["2157"] = 67,
	["2158"] = 51,
	["2159"] = 61,
	["2160"] = 69,
	["2161"] = 61,
	["2162"] = 69,
	["2163"] = 80,
	["2164"] = 27,
	["2166"] = 37,
	["2168"] = 41,
	["2170"] = 45,
	["2178"] = 9999,
	["2179"] = 9999,
	["2180"] = 9999,
	["2181"] = 9999,
	["2182"] = 9999,
	["2183"] = 9999,
	["2184"] = 9999,
	["2185"] = 9999,
	["2186"] = 9999,
	["2187"] = 9999,
	["2188"] = 9999,
	["2189"] = 9999,
	["2190"] = 9999,
	["2191"] = 9999,
	["2192"] = 9999,
	["2193"] = 9999,
	["2194"] = 9999,
	["2196"] = 9999,
	["2197"] = 9999,
	["2198"] = 9999,
	["2199"] = 9999,
	["2200"] = 9999,
	["2201"] = 9999,
	["2202"] = 9999,
	["2203"] = 9999
}
p.enemyFighterPowerDataTb2 = {
	["1505"] = 1,
	["1506"] = 1,
	["1507"] = 1,
	["1509"] = 1,
	["1511"] = 1,
	["1518"] = 1,
	["1519"] = 1,
	["1520"] = 1,
	["1522"] = 2,
	["1527"] = 2,
	["1529"] = 2,
	["1541"] = 2,
	["1543"] = 2,
	["1555"] = 1,
	["1566"] = 4,
	["1567"] = 4,
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
	["1790"] = 2,
	["1791"] = 2,
	["1792"] = 2,
	["1793"] = 2,
	["1794"] = 2,
	["1795"] = 2,
	["1796"] = 2,
	["1797"] = 2,
	["1798"] = 2,
	["1862"] = 1,
	["1863"] = 4,
	["1864"] = 4,
	["1895"] = 4,
	["1896"] = 4,
	["1897"] = 4,
	["1898"] = 4,
	["1899"] = 4,
	["1900"] = 4,
	["1901"] = 4,
	["1902"] = 4,
	["1903"] = 4,
	["1998"] = 12,
	["2007"] = 12,
	["2008"] = 14,
	["2010"] = 17,
	["2011"] = 19,
	["2014"] = 14,
	["2031"] = 14,
	["2033"] = 24,
	["2034"] = 42,
	["2038"] = 14,
	["2039"] = 14,
	["2040"] = 14,
	["2090"] = 4
}
return p
