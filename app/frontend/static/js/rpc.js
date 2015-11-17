var Status = function() {
  this.code_ = Status.Code.NONE;
  this.message_ = null ;
};


Status.Code = {
  NONE: 0,
  LOADING: 1,
  SUCCESS: 2,
  ERROR: -1
};


Status.prototype.getMessage = function() {
  if (!this.code_) {
    return null;
  } else if (this.message_) {
    return this.message_;
  } else {
    switch (this.code_) {
      case Status.Code.LOADING:
        return 'Loading...';
        break;
      case Status.Code.SUCCESS:
        return 'Done!'; 
        break;
      case Status.Code.ERROR:
        return 'Error';
        break;
    };
  }
};


Status.prototype.setCode = function(code, opt_message) {
  this.code_ = code;
  this.message_ = (opt_message != undefined) ? opt_message : null;
};


Status.prototype.getCode = function() {
  return this.code_;
};
