// d3.csv('https://raw.githubusercontent.com/bcdunbar/datasets/master/parcoords_data.csv', function(err, rows){

// function unpack(rows, key) {
//   return rows.map(function(row) {
//     return row[key];
//   });
// }

// var data = [{
//   type: 'parcoords',
// //   line: {
// //     // showscale: true,
// //     // reversescale: true,
// //     // colorscale: 'Jet',
// //     // cmin: -4000,
// //     // cmax: -100
// //     // ,
// //     // color: unpack(rows, 'colorVal')
// //   },

//   dimensions: [{
// //     constraintrange: [100000, 150000],
// //     range: [32000, 227900],
// //     label: 'Block height',
// //     values: unpack(rows, 'blockHeight')
// //   }, {
//     range: [0, 700000],
//     label: 'Block width',
//     values: unpack(rows, 'blockWidth')
//   }, {
//     label: 'Cylinder material',
//     tickvals: [0, 0.5, 1, 2, 3],
//     // ticktext: ['A', 'AB', 'B', 'Y', 'Z'],
//     values: unpack(rows, 'cycMaterial')
//   }, {
//     label: 'Block material',
//     // tickvals: [0, 1, 2, 3],
//     range: [-1, 4],
//     values: unpack(rows, 'blockMaterial')
//   }, {
//     range: [134, 3154],
//     label: 'Total weight',
//     // visible: true,
//     values: unpack(rows, 'totalWeight')
//   }, {
//     range: [9, 19984],
//     label: 'Assembly penalty weight',
//     values: unpack(rows, 'assemblyPW')
//   }, {
//     range: [49000, 568000],
//     label: 'Height st width',
//     values: unpack(rows, 'HstW')
//   }, {
//     range: [-28000, 196430],
//     label: 'Min height width',
//     values: unpack(rows, 'minHW')
//   }, {
//      range: [98453, 501789],
//      label: 'Min width diameter',
//      values: unpack(rows, 'minWD')
//   }, {
//     range: [1417, 107154],
//     label: 'RF block',
//     values: unpack(rows, 'rfBlock')
//   }]
// }];

// // Plotly.newPlot('myDiv', data);

// });

// let json_g = null

let qUI = $('<select>')
let aBegin = $('<select>')
let aEnd = $('<select>')
$('#form').append(qUI, aBegin, aEnd)
QuranData.Sura.forEach((s, sI) => {
    // console.log(s, sI)
    if (s.length > 4) {
        qUI.append($('<option>', {
            value: sI-1,
            text: s[4]
        }))
    }
});

qUI.change(function() {
    let sIndex = parseInt(qUI.find('option:selected').val())
    aBegin.find('option').remove()
    aEnd.find('option').remove()
    Array.from(Array(QuranData.Sura[sIndex+1][1]).keys()).forEach(function(a) {
        aBegin.append($('<option>', {
            value: a,
            text: a+1
        }))
        aEnd.append($('<option>', {
            value: a,
            text: a+1
        }))
    })
    aEnd.find('option').last().attr('selected','selected')
})

qUI.change()

let add = $('<span>')
    .text('+')
    .attr('class', 'button')
    // .attr('display', 'inline')
    .click(function() {
        let sIndex = parseInt(qUI.find('option:selected').val())
        let ab = parseInt(aBegin.find('option:selected').val())
        let ae = parseInt(aEnd.find('option:selected').val())
        addToList(sIndex, ab, ae)
    })
$('#form').append(add)


let list = $('<ul>').attr('id', 'sortable')
list.sortable()
list.disableSelection()   

function addToList(sIndex, ab, ae) {
    let li = $('<li>').text(QuranData.Sura[sIndex+1][4] + ': ' + (ab+1) + '-' + (ae+1))
    .attr('s', sIndex)
    .attr('ab', ab)
    .attr('ae', ae)
    .click(function() {
        $(this).remove()
    })
    list.append(li)
}

let listContainer = $('<div>').attr('id', 'list-container')
$('#form').append(listContainer)
listContainer.append(list)

let root_typeUI = $('<select>')
    .append($('<option>', {
        value: 0,
        text: 'ریشه'
    }))
    .append($('<option>', {
        value: 1,
        text: 'لم'
    }))
$('#form').append(root_typeUI)

let min_nonpresent_cntUI = $('<input>')
    .attr('type', 'text')
    .attr('class', 'number')
    .val(0)
    .spinner()
$('#form').append(min_nonpresent_cntUI)

let draw = $('<span>')
    .attr('id', 'draw')
    .attr('class', 'button')
    .text('ترسیم')
    .click(redraw)
$('#form').append(draw)

let json_g = null

function redraw() {
    let range_list = list.find('li').map(function(e, ee) {
        ee = $(ee)
        // console.log(e, ee.attr('s'), ee.attr('ab'), ee.attr('ae'))
        return '[' + [ee.attr('s'), ee.attr('ab'), ee.attr('ae')].join(',') + ']'
    })
    // console.log(range_list)
    let ranges = '[' + range_list.get().join(',') + ']'
    let root_type = parseInt(root_typeUI.find('option:selected').val())
    let min_nonpresent_cnt = parseInt(min_nonpresent_cntUI.val())
    // console.log(ranges)
    x = d3.json('https://q.foroughmand.ir/common_roots/ranges=' + ranges + '&min_nonpresent_cnt=' + min_nonpresent_cnt + '&root_type=' + root_type + '&ret_instances=0', function(err, json) {
        // console.log(json)
        // json_g = json
        
        if (json.length == 0) {
            return;
        }

        json_g = json
        

        let roots = [...new Set([].concat(...json.map(function(row) { return Object.keys(row['rf']) })))]
        let rootFreqSum = Object.fromEntries(roots.map(r => [r, json.reduce((ps,row) => ps + (r in row.rf ? row.rf[r] : 0), 0)]))
        let maxValueAll = Math.max(...json.map(function(row) {return Math.max(...Object.values(row.rf))}))
        roots.sort((a, b) => - rootFreqSum[a] + rootFreqSum[b])
        
        var data = [{
            type: 'parcoords',
            labelangle: 90,
            line: {
            //   showscale: true,
            //   reversescale: true,
              colorscale: 'Jet',
            //   cmin: -4000,
            //   cmax: -100
            //   ,
              color: Array.from(Array(json.length).keys()).map(x=>x+1),
            },
          
            dimensions: [{
                range: [0, maxValueAll],
                label: 'محدوده‌ها',
                showscale: true,
                values: Array.from(Array(json.length).keys()).map(x=>x*maxValueAll/json.length),
                tickvals: Array.from(Array(json.length).keys()).map(x=>x*maxValueAll/json.length),
                ticktext: json.map(function(row) { 
                    return QuranData.Sura[row.range[0]+1][4] + ': ' + (row.range[1]+1) + '-' + (row.range[2]+1);
                })
            }].concat(roots.map(function(root) {
                let values = json.map(function(row) {return root in row.rf ? row.rf[root] : 0;})
                return {
                    // range: [0, Math.max(...values)], 
                    range: [0, maxValueAll], 
                    label: root,
                    tickvals: [...new Set(values)].sort(),
                    values: values
                };
            }))
          }]
        
        // console.log(data)
        
        Plotly.newPlot('myDiv', data);
        
    })
}

$( function() {
    //test
    addToList(2, 0, 199) 
    addToList(19, 0, 134)
    addToList(0, 0, 6)
    redraw()

})