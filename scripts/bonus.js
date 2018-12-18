const path = require('path')
const fs = require('fs')
const bonusList = require('../KCKit/src/data/bonus')

const allBonus = {}
const OUTPUT_DIR = path.join(__dirname, '../db/bonus.json')

for (let _bonus of bonusList) {
  const bonus = {
    'ship': {}
  }
  let id = null
  let star = 0
  let combined = []
  const include = {}
  const exclude = {}
  if ('equipment' in _bonus) {
    id = _bonus['equipment']
  } else if ('list' in _bonus) {
    const list = _bonus['list']
    combined = list.splice(1).map(c => {
      if (c === 'SurfaceRadar') {
        return '对水面雷达/电探'
      } else if (c === 'AARadar') {
        return '对空雷达/电探'
      }
      return c
    })
    if (Number.isInteger(list[0])) {
      id = list[0]
    } else {
      id = list[0]['id']
      star = list[0]['star']
    }
  }
  if (!id) {
    continue
  }
  bonus['star'] = star
  bonus['combined'] = combined
  for (let key in _bonus['ship']) {
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
        include['class'] = include['class'].concat(_bonus['ship']['isClass'])
        break
      case 'isNotClass':
        if (!('class' in exclude)) {
          exclude['class'] = []
        }
        exclude['class'] = exclude['class'].concat(_bonus['ship']['isNotClass'])
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
  if (!(id in allBonus)) {
    allBonus[id] = []
  }
  allBonus[id].push(bonus)
}

fs.writeFile(OUTPUT_DIR, JSON.stringify(allBonus), err => {
  if (err) {
    console.error(err)
    process.exit(1)
  }
  console.log('bonus.json generated successfully!')
})
