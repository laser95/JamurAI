const courseFileType = 'race course 2018';

var unitSize;
const maxUnitSize = 100;
const minUnitSize = 5;

const courseMargin = 6;

function zoom(diff) {
  var newSize = (1+diff/10) * unitSize;
  if (newSize < minUnitSize || maxUnitSize < newSize) return;
  unitSize = newSize;
  drawCourse();
}

function standardView() {
  courseView = document.getElementById('courseView');
  unitSize = (courseView.clientWidth-2*courseMargin)/courseWidth;
  drawCourse();
}

function wholeView() {
  courseView = document.getElementById('courseView');
  unitSize =
    Math.min((courseView.clientWidth-2*courseMargin)/courseWidth,
	     (courseView.clientHeight-2*courseMargin)/courseLength);
  drawCourse();
}

var courseLength;
var courseWidth;
var minSize = 5;
var maxSize = 100;

var squares;
var startPos = [0, 1];
var course;
var visionScreen;

function widerCourse() {
  if (courseWidth == maxSize) return;
  for (var y = 0; y != courseLength; y++) {
    var sqr = buildSquare(courseWidth, y);
    squares[y].push(sqr);
    course.appendChild(sqr);
  }
  courseWidth += 1;
  standardView();
}

function narrowerCourse() {
  if (courseWidth == minSize) return;
  for (var y = 0; y != courseLength; y++) {
    course.removeChild(squares[y].pop());
  }
  courseWidth -= 1;
  standardView();
}

function longerCourse() {
  if (courseLength == maxSize) return;
  squares.push([]);
  for (var x = 0; x != courseWidth; x++) {
    var sqr = buildSquare(x, courseLength);
    squares[courseLength].push(sqr);
    course.appendChild(sqr);
  }
  courseLength += 1;
  standardView();
}

function shorterCourse() {
  if (courseLength == minSize) return;
  for (var x = 0; x != courseWidth; x++) {
    course.removeChild(squares[courseLength-1][x]);
  }
  squares.pop();
  courseLength -= 1;
  standardView();
}

function loadFile(evt) {
  if (evt.target.files.length === 0) return;
  var file = evt.target.files[0];
  var reader = new FileReader();
  reader.onload =
    function(ev) {
      var data = JSON.parse(ev.target.result);
      if (data.filetype != courseFileType) {
	alert('The file does not contain a SamurAI Jockey 2018 race course');
      } else {
	document.getElementById("visionRange").value = data.vision;
	document.getElementById("thinkTime").value = data.thinkTime;
	document.getElementById("stepLimit").value = data.stepLimit;
	startPos[0] = data.x0;
	startPos[1] = data.x1;
	newCourse(data.width, data.length);
	var x = 0, y = 0;
	data.squares.forEach(function (s) {
	  squares[y][x].state = s;
	  x ++;
	  if (x == data.width) {
	    x = 0; y++;
	  }
	});
	squares[0][data.x0].state = 3;
	squares[0][data.x1].state = 4;
      }
      standardView();
    };
  reader.readAsText(file);
}

function saveFile(evt) {
  courseData = encodeCourse();
  parent.document.getElementById('saveFileForm').style.display = 'block';
  parent.document.getElementById('saveFileName').focus();
}

function doSaveFile(evt) {
  var fileName = parent.document.getElementById("saveFileName").value;
  parent.document.getElementById('saveFileForm').style.display = 'none';
  var file =
      new Blob([JSON.stringify(courseData)], {type: 'application/json'});
  if (window.navigator.msSaveOrOpenBlob) {// IE10+
    window.navigator.msSaveOrOpenBlob(file, fileName);
  } else { // Others
    var a = parent.document.createElement("a"),
        url = URL.createObjectURL(file);
    a.href = url;
    a.download = fileName;
    parent.document.body.appendChild(a);
    a.click();
    setTimeout(function() {
      parent.document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 0);
  }
}

function writeFile(evt) {
  parent.document.getElementById('writeFileForm').style.display = 'block';
  parent.document.getElementById('writeFileName').focus();
}

function encodeCourse() {
  var squareKinds = [];
  for (var y = 0; y != courseLength; y++) {
    for (var x = 0; x != courseWidth; x++) {
      var s = squares[y][x].state;
      if (s > 2) s = 0;
      squareKinds.push(s);
    }
  }
  return {
    "filetype": courseFileType,
    "width": courseWidth,
    "length": courseLength,
    "vision": parseInt(document.getElementById("visionRange").value),
    "thinkTime": parseInt(document.getElementById("thinkTime").value),
    "stepLimit": parseInt(document.getElementById("stepLimit").value),
    "x0": startPos[0],
    "x1": startPos[1],
    "squares": squareKinds
  };
}
  
function doWriteFile(evt) {
  var fileName = parent.document.getElementById("writeFileName").value;
  parent.document.getElementById('writeFileForm').style.display = 'none';
  var file = new Blob([JSON.stringify(encodeCourse())], {type: 'application/json'});
  if (window.navigator.msSaveOrOpenBlob) {// IE10+
    window.navigator.msSaveOrOpenBlob(file, fileName);
  } else { // Others
    var a = parent.document.createElement("a"),
        url = URL.createObjectURL(file);
    a.href = url;
    a.download = fileName;
    parent.document.body.appendChild(a);
    a.click();
    setTimeout(function() {
      parent.document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 0);
  }
}

function editCourse(evt) {
  courseBeingEdited = !courseBeingEdited;
  if (courseBeingEdited) {
    polygons.style.display = 'block';
    evt.target.innerHTML = 'Done';
  } else {
    polygons.style.display = 'none';
    evt.target.innerHTML = 'Edit';
  }
}

const squareIcons = [
  "../icons/lawn.png",
  "../icons/obst.png",
  "../icons/jump.png",
  "../icons/withPlayer0.png",
  "../icons/withPlayer1.png"
];

function positionSquare(sqr) {
  sqr.style.width = unitSize - 2 + "px";
  sqr.style.height = unitSize - 2 + "px";
  sqr.style.top =
    (courseLength-sqr.yy-1)*unitSize + courseMargin + 1 + "px";
  sqr.style.left = sqr.xx*unitSize + courseMargin + 1 + "px";
  sqr.src = squareIcons[sqr.state];
}

function buildSquare(x, y) {
  const sqr = document.createElement('img');
  const style = sqr.style;
  sqr.setAttribute('onmouseenter', "mouseEnteredSquare(this)");
  sqr.setAttribute('onmouseleave', "mouseLeftSquare(this)");
  sqr.setAttribute('onmousedown', "mouseDownOnSquare(this)");
  sqr.setAttribute('title', "("+x+","+y+")");
  sqr.xx = x;
  sqr.yy = y;
  sqr.state = 0;
  for (var p = 0; p != 2; p++) {
    if (y == 0 && startPos[p] == x) sqr.state = 3 + p;
  }
  sqr.draggable = false;
  sqr.className = "courseSquare";
  return sqr;
}

var stateChangedTo = null;
var prevSquare;
window.onmouseup = function (event) { stateChangedTo = null; }

function mouseEnteredSquare(sqr) {
  changeSquareState(sqr);
  const visionRange = document.getElementById("visionRange").value;
  visionScreen.style.height =
    (courseLength - sqr.yy - visionRange) * unitSize
    + courseMargin + 1 + "px";
}

function mouseLeftSquare(sqr) {
  visionScreen.style.height = "0px";
}

function mouseDownOnSquare(sqr) {
  if (sqr.state < 3) {
    stateChangedTo = (sqr.state+1)%3;
    changeSquareState(sqr);
  } else {
    stateChangedTo = sqr.state;
    prevSquare = sqr;
  }
}

function changeSquareState(sqr) {
  if (stateChangedTo != null && sqr.state != stateChangedTo) {
    if (stateChangedTo >= 3) {
      if (sqr.yy != 0 ||	  // Start position should be at y=0
	  sqr.state != 0) {	  // and empty without obstacles
	return;
      }
      startPos[stateChangedTo-3] = sqr.xx;
      prevSquare.state = 0;
      prevSquare.src = squareIcons[0];
      prevSquare = sqr;
    }
    sqr.state = stateChangedTo;
    sqr.src = squareIcons[sqr.state];
  }
}

function drawCourse() {
  const courseView = document.getElementById('courseView');
  const controlBox = document.getElementById('controlBox');
  courseView.style.height =
    window.innerHeight - controlBox.offsetHeight + "px";
  course.style.height =
    courseLength*unitSize + 2*courseMargin + "px";
  course.style.width =
    courseWidth*unitSize + 2*courseMargin + "px";
  for (var y = 0; y != courseLength; y++) {
    for (var x = 0; x != courseWidth; x++) {
      positionSquare(squares[y][x]);
    }
  }
  document.getElementById("courseSize").innerHTML =
    courseWidth + "&times;" + courseLength;
  const visionRange = document.getElementById('visionRange');
  visionRange.max = courseLength;
  visionRange.value = Math.min(visionRange.value, courseLength-1);
  visionScreen.style.height = "0px";
  visionScreen.style.width = course.style.width;
  visionScreen.style.display = "block"
}

function windowResized() {
  standardView();
}

function newCourse(width, length) {
  course = document.getElementById('course');
  course.innerHTML = '';
  courseWidth = width;
  courseLength = length;
  squares = [];
  for (var y = 0; y != courseLength; y++) {
    squares[y] = [];
    for (var x = 0; x != courseWidth; x++) {
      const sqr = buildSquare(x, y);
      course.appendChild(sqr);
      squares[y][x] = sqr;
    }
  }
  visionScreen = document.createElement('img');
  visionScreen.id = 'visionScreen';
  course.appendChild(visionScreen);
  standardView();
}
