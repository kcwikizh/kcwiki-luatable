const path = require('path')
const fs = require('fs')
const bonusList = require('../KCKit/src/data/bonus')

const allBonus = {}
const OUTPUT_DIR = path.join(__dirname, '../db/bonus.json')

/**
 * @template T
 * @param {T|T[]|undefined} item
 * @returns {T[]} 
 */
function packToArray(item) {
  if (item === undefined) return [] 
  if (!Array.isArray(item)) return [item] 
  return item 
}

/**
 * @template T
 * @param {(T|T[])[]} item
 * @returns {T[]} 
 */
function unpackArray(item) {
  return [].concat(...item)
}

const EQUIPMENT_RANK = [
  'isID', 'has', 'hasID', 'hasOneOf'
]

function getRank(key) {
  const index = EQUIPMENT_RANK.indexOf(key) 
  if (index < 0) return Infinity 
  return index 
}

/**
 * 
 * @param {Extract<typeof bonusList[number]['equipments'], Array>[number]} condition
 * @returns {{ id: number, star?: number }[]|null}
 */
function extractCondition(condition) {
  if ('isID' in condition) {
    const ids = packToArray(condition['isID']) 
    return ids.map(((id) => {
      if ('improvement' in condition) {
        return { id, star: condition['improvement'] }
      }
      return { id }
    }))
  }
  if ('has' in condition) {
    return [{ id: condition['has']['id'], star: condition['has']['star'] }]
  }
  if ('hasOneOf' in condition) {
    return condition['hasOneOf'].map((e) => ({ id: e['isID'] }))
  }
  if ('isOneOf' in condition) {
    return unpackArray(condition['isOneOf'].map((e) => e['isID'].map((e => ({ id: e })))))
  }
  return null 
}

/**
 * 
 * @param {Extract<typeof bonusList[number]['equipments'], Array>} conditions
 */
function extractComplexEquipment(conditions) {
  const [main, ...rest] = conditions
  const equipments = extractCondition(main)
  if (!equipments) {
    return []
  }
  const combined = rest.map((condition) => {
    if (condition['hasSurfaceRadar']) {
      return '对水面雷达/电探'
    }
    if (condition['isSurfaceRadar']) {
      return '对水面雷达/电探'
    }
    if (condition['hasAARadar']) {
      return '对空雷达/电探'
    }
    if (condition['isAARadar']) {
      return '对空雷达/电探'
    }
    if (condition['hasAAGuns']) {
      return '对空机枪'
    }
    if (condition['isSurfaceShipPersonnel']) {
      return '水上舰要员'
    }
    const equipments = extractCondition(condition) 
    if (equipments) {
      const ids = equipments.map((e) => {
        if (Object.keys(e).length === 1) {
          return e.id
        }
        return e
      }) 
      if (ids.length === 1) {
        return ids[0]
      } else {
        return ids
      }
    }
    return condition 
  }) 
  return equipments.map((equipment) => {
    return {
      ...equipment,
      combined: combined.length ? combined : void 0
    } 
  }) 
} 

/**
 * 
 * @param {typeof bonusList[number]} bonus 
 */
function extractEquipments(bonus) {
  if ('equipment' in bonus) {
    return [{ id: bonus['equipment'] }]
  }
  if ('equipments' in bonus) {
    let equipments = bonus['equipments']
    // 分解单个 equipments 字段
    if (!Array.isArray(equipments)) {
      const realEquipments = []
      if ('hasID' in equipments) {
        const { hasID, ...rest } = equipments
        realEquipments.push(...hasID.map(e => ({ isID: e })))
        equipments = rest
      }
      const keys = Object.entries(equipments)
      const sortedKeys = keys.sort((a, b) => getRank(a[0]) - getRank(b[0]))
      realEquipments.push(...sortedKeys.map(([k, v]) => ({ [k]: v })))
      equipments = realEquipments
    }
    return extractComplexEquipment(equipments)
  }
  return [] 
}

for (const _bonus of bonusList) {
  const equipments = extractEquipments(_bonus) 
  equipments.forEach((equipment) => {
    const bonus = {
      ship: {},
      star: equipment['star'] || 0,
      combined: equipment['combined'] || [],
    }
    const include = {}
    const exclude = {}
    for (const key in _bonus['ship']) {
      switch (key) {
        case 'isID':
          if (!('id' in include)) {
            include['id'] = []
          }
          include['id'] = include['id'].concat(_bonus['ship']['isID'])
          break
        case 'isNotID':
          if (!('id' in exclude)) {
            exclude['id'] = []
          }
          exclude['id'] = exclude['id'].concat(_bonus['ship']['isNotID'])
          break
        case 'isType':
          if (!('type' in include)) {
            include['type'] = []
          }
          include['type'] = include['type'].concat(_bonus['ship']['isType'])
          break
        case 'isNotType':
          if (!('type' in exclude)) {
            exclude['type'] = []
          }
          exclude['type'] = exclude['type'].concat(_bonus['ship']['isNotType'])
          break
        case 'isClass':
          if (!('class' in include)) {
            include['class'] = []
          }
          const clzList1 = _bonus['ship']['isClass'] 
          if (Array.isArray(clzList1[0])) {
              include['class'] = include['class'].concat(...clzList1) 
  
          } else {
              include['class'] = include['class'].concat(clzList1) 
          }
          break
        case 'isNotClass':
          if (!('class' in exclude)) {
            exclude['class'] = []
          }
          const clzList2 = _bonus['ship']['isNotClass'] 
          if (Array.isArray(clzList2[0])) {
              exclude['class'] = exclude['class'].concat(...clzList2) 
  
          } else {
              exclude['class'] = exclude['class'].concat(clzList2) 
          }
          break
        default:
          break
      }
    }
    bonus['ship']['include'] = include
    bonus['ship']['exclude'] = exclude
    let bns = {
      type: '-',
      bonus: {}
    }
    if ('bonus' in _bonus) {
      bns['bonus'] = _bonus['bonus']
    } else if ('bonusCount' in _bonus) {
      bns['type'] = 'count'
      bns['bonus'] = _bonus['bonusCount']
    } else if ('bonusImprove' in _bonus) {
      bns['type'] = 'improve'
      bns['bonus'] = _bonus['bonusImprove']
    } else if ('bonusArea' in _bonus) {
      bns['type'] = 'area'
      bns['bonus'] = _bonus['bonusArea']
    }
    bonus['bonus'] = bns
    if ('bonusAccumulate' in _bonus) {
      bonus['accumulate'] = _bonus['bonusAccumulate']
    }
    if (!equipment['id']) {
      return 
    }
    const id = equipment['id'] 
    if (!(id in allBonus)) {
      allBonus[id] = []
    }
    allBonus[id].push(bonus)
  }) 
}

fs.writeFile(OUTPUT_DIR, JSON.stringify(allBonus), err => {
  if (err) {
    console.error(err)
    process.exit(1)
  }
  console.log('bonus.json generated successfully!')
})
