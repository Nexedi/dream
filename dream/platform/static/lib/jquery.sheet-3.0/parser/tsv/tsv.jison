/* description: Parses a tab separated value to an array */

/* lexical grammar */
%lex
%s SINGLE_QUOTATION_ON DOUBLE_QUOTATION_ON INITIAL
%%

/* single quote handling*/
<SINGLE_QUOTATION_ON>(\n|"\n")      {return 'CHAR';}
<SINGLE_QUOTATION_ON>'"'            {return 'CHAR';}
<SINGLE_QUOTATION_ON>"'" {
	this.popState();
	return 'SINGLE_QUOTATION';
}
<SINGLE_QUOTATION_ON>(?=(\t)) {
	this.popState();
	return 'FAKE_DOUBLE_QUOTATION';
}
<INITIAL>("'") {
	this.begin('SINGLE_QUOTATION_ON');
	return 'SINGLE_QUOTATION';
}
([\t\n]"'") {
	this.begin('SINGLE_QUOTATION_ON');
	return 'SINGLE_QUOTATION';
}

/* double quote handling*/
<DOUBLE_QUOTATION_ON>(\n|"\n")      {return 'CHAR';}
<DOUBLE_QUOTATION_ON>"'"            {return 'CHAR';}
<DOUBLE_QUOTATION_ON>'"' {
	this.popState();
	return 'DOUBLE_QUOTATION';
}
<DOUBLE_QUOTATION_ON>(?=(\t)) {
	this.popState();
	return 'FAKE_DOUBLE_QUOTATION';
}
<INITIAL>('"') {

 	this.begin('DOUBLE_QUOTATION_ON');
 	return 'DOUBLE_QUOTATION';
}
([\t\n]'"') {
	this.begin('DOUBLE_QUOTATION_ON');
	return 'DOUBLE_QUOTATION';
}

/*spreadsheet control characters*/
(\n|"\n")                           {return 'END_OF_LINE';}
(\t)                                {return 'COLUMN';}
(\s)								{return 'CHAR';}
.                                   {return 'CHAR';}
<<EOF>>								{return 'EOF';}


/lex

%start cells

%% /* language grammar */

cells :
	string EOF {
        return $1;
    }
	| rows EOF {
        return $1;
    }
    | EOF {
        return '';
    }
;

rows :
	row {
		$$ = [$1];
	}
	| rows row {
		$1 = $1 || [];
		$1.push($2);
	}
;

row :
	END_OF_LINE {
		$$ = [];
	}
	| column {
		$$ = [$1];
	}
	| row column {
		$1 = $1 || [];
		$1.push($2);
		$$ = $1;
	}
;

column :
	COLUMN {
		$$ = '';
	}
	| string {
		$$ = $1;
    }
    | string COLUMN {
        $$ = $1;
    }
;

string :
	DOUBLE_QUOTATION chars FAKE_DOUBLE_QUOTATION {
		$$ = $2 + $3;
	}
	| SINGLE_QUOTATION chars FAKE_SINGLE_QUOTATION {
		$$ = $2 + $3;
	}
	| DOUBLE_QUOTATION chars DOUBLE_QUOTATION {
		$$ = $2;
	}
	| SINGLE_QUOTATION chars SINGLE_QUOTATION {
		$$ = $2;
	}
	| chars {
		$$ = $1;
	}
;

chars :
	CHAR {
		$$ = $1;
	}
	| chars CHAR {
		$$ = $1 + $2;
	}
;