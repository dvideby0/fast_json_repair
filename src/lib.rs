use pyo3::prelude::*;
use std::collections::VecDeque;

#[derive(Debug, Clone, PartialEq)]
enum Token {
    LeftBrace,
    RightBrace,
    LeftBracket,
    RightBracket,
    Comma,
    Colon,
    String(String),
    Number(String),
    True,
    False,
    Null,
    EOF,
}

struct Lexer {
    input: Vec<char>,
    position: usize,
    current_char: Option<char>,
}

impl Lexer {
    fn new(input: &str) -> Self {
        let chars: Vec<char> = input.chars().collect();
        let current_char = if chars.is_empty() {
            None
        } else {
            Some(chars[0])
        };
        
        Lexer {
            input: chars,
            position: 0,
            current_char,
        }
    }
    
    fn advance(&mut self) {
        self.position += 1;
        if self.position < self.input.len() {
            self.current_char = Some(self.input[self.position]);
        } else {
            self.current_char = None;
        }
    }
    
    fn skip_whitespace(&mut self) {
        while let Some(ch) = self.current_char {
            if ch.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }
    
    fn read_string(&mut self, quote_char: char) -> String {
        let mut result = String::new();
        self.advance(); // Skip opening quote
        
        while let Some(ch) = self.current_char {
            if ch == quote_char {
                self.advance(); // Skip closing quote
                break;
            } else if ch == '\\' {
                self.advance();
                if let Some(escaped) = self.current_char {
                    match escaped {
                        'n' => result.push('\n'),
                        'r' => result.push('\r'),
                        't' => result.push('\t'),
                        'b' => result.push('\u{0008}'),
                        'f' => result.push('\u{000C}'),
                        '"' => result.push('"'),
                        '\'' => result.push('\''),
                        '\\' => result.push('\\'),
                        '/' => result.push('/'),
                        'u' => {
                            // Handle unicode escape
                            self.advance();
                            let mut hex = String::new();
                            for _ in 0..4 {
                                if let Some(h) = self.current_char {
                                    if h.is_ascii_hexdigit() {
                                        hex.push(h);
                                        self.advance();
                                    } else {
                                        break;
                                    }
                                } else {
                                    break;
                                }
                            }
                            if hex.len() == 4 {
                                if let Ok(code) = u32::from_str_radix(&hex, 16) {
                                    if let Some(unicode_char) = char::from_u32(code) {
                                        result.push(unicode_char);
                                    } else {
                                        // Invalid unicode, keep as is
                                        result.push_str("\\u");
                                        result.push_str(&hex);
                                    }
                                } else {
                                    result.push_str("\\u");
                                    result.push_str(&hex);
                                }
                            } else {
                                // Incomplete unicode escape, treat as literal
                                result.push_str("\\u");
                                result.push_str(&hex);
                            }
                            continue; // Don't advance again
                        }
                        _ => {
                            result.push(escaped);
                        }
                    }
                    self.advance();
                } else {
                    // Trailing backslash
                    result.push('\\');
                }
            } else {
                result.push(ch);
                self.advance();
            }
        }
        
        result
    }
    
    fn read_unquoted_string(&mut self) -> String {
        let mut result = String::new();
        
        while let Some(ch) = self.current_char {
            if ch.is_alphanumeric() || ch == '_' || ch == '-' || ch == '.' || ch == '$' {
                result.push(ch);
                self.advance();
            } else if ch == ':' || ch == ',' || ch == '}' || ch == ']' || ch.is_whitespace() {
                break;
            } else {
                result.push(ch);
                self.advance();
            }
        }
        
        result
    }
    
    fn read_number(&mut self) -> String {
        let mut result = String::new();
        
        // Handle negative numbers
        if self.current_char == Some('-') {
            result.push('-');
            self.advance();
        }
        
        // Read integer part
        while let Some(ch) = self.current_char {
            if ch.is_ascii_digit() {
                result.push(ch);
                self.advance();
            } else {
                break;
            }
        }
        
        // Handle decimal point
        if self.current_char == Some('.') {
            result.push('.');
            self.advance();
            
            // Read fractional part
            while let Some(ch) = self.current_char {
                if ch.is_ascii_digit() {
                    result.push(ch);
                    self.advance();
                } else {
                    break;
                }
            }
        }
        
        // Handle scientific notation
        if let Some(ch) = self.current_char {
            if ch == 'e' || ch == 'E' {
                result.push(ch);
                self.advance();
                
                if let Some(sign) = self.current_char {
                    if sign == '+' || sign == '-' {
                        result.push(sign);
                        self.advance();
                    }
                }
                
                while let Some(ch) = self.current_char {
                    if ch.is_ascii_digit() {
                        result.push(ch);
                        self.advance();
                    } else {
                        break;
                    }
                }
            }
        }
        
        result
    }
    
    fn next_token(&mut self) -> Token {
        self.skip_whitespace();
        
        match self.current_char {
            None => Token::EOF,
            Some('{') => {
                self.advance();
                Token::LeftBrace
            }
            Some('}') => {
                self.advance();
                Token::RightBrace
            }
            Some('[') => {
                self.advance();
                Token::LeftBracket
            }
            Some(']') => {
                self.advance();
                Token::RightBracket
            }
            Some(',') => {
                self.advance();
                Token::Comma
            }
            Some(':') => {
                self.advance();
                Token::Colon
            }
            Some('"') => Token::String(self.read_string('"')),
            Some('\'') => Token::String(self.read_string('\'')),
            Some('-') | Some('0'..='9') => Token::Number(self.read_number()),
            Some(_) => {
                // Try to read as unquoted string/keyword
                let word = self.read_unquoted_string();
                
                match word.as_str() {
                    "true" => Token::True,
                    "false" => Token::False,
                    "null" => Token::Null,
                    "True" => Token::True,  // Python boolean
                    "False" => Token::False, // Python boolean
                    "None" => Token::Null,   // Python None
                    _ => {
                        // Check if it looks like a number
                        if word.chars().all(|c| c.is_ascii_digit() || c == '.' || c == '-' || c == 'e' || c == 'E' || c == '+') {
                            if word.parse::<f64>().is_ok() {
                                Token::Number(word)
                            } else {
                                Token::String(word)
                            }
                        } else {
                            Token::String(word)
                        }
                    }
                }
            }
        }
    }
}

struct Parser {
    tokens: VecDeque<Token>,
    current_token: Token,
    depth: usize,
    max_depth: usize,
}

impl Parser {
    fn new(input: &str) -> Self {
        let mut lexer = Lexer::new(input);
        let mut tokens = VecDeque::new();
        
        loop {
            let token = lexer.next_token();
            if token == Token::EOF {
                tokens.push_back(token);
                break;
            }
            tokens.push_back(token);
        }
        
        let current_token = tokens.pop_front().unwrap_or(Token::EOF);
        
        Parser {
            tokens,
            current_token,
            depth: 0,
            max_depth: 1000,
        }
    }
    
    fn advance(&mut self) {
        self.current_token = self.tokens.pop_front().unwrap_or(Token::EOF);
    }
    
    fn parse(&mut self) -> Result<serde_json::Value, String> {
        self.parse_value()
    }
    
    fn parse_value(&mut self) -> Result<serde_json::Value, String> {
        match &self.current_token {
            Token::LeftBrace => self.parse_object(),
            Token::LeftBracket => self.parse_array(),
            Token::String(s) => {
                let val = serde_json::Value::String(s.clone());
                self.advance();
                Ok(val)
            }
            Token::Number(n) => {
                let val = n.parse::<f64>()
                    .map(|f| serde_json::Value::Number(serde_json::Number::from_f64(f).unwrap_or(serde_json::Number::from(0))))
                    .unwrap_or(serde_json::Value::Number(serde_json::Number::from(0)));
                self.advance();
                Ok(val)
            }
            Token::True => {
                self.advance();
                Ok(serde_json::Value::Bool(true))
            }
            Token::False => {
                self.advance();
                Ok(serde_json::Value::Bool(false))
            }
            Token::Null => {
                self.advance();
                Ok(serde_json::Value::Null)
            }
            Token::EOF => Ok(serde_json::Value::Null),
            _ => {
                // Unexpected token, try to recover
                self.advance();
                Ok(serde_json::Value::Null)
            }
        }
    }
    
    fn parse_object(&mut self) -> Result<serde_json::Value, String> {
        self.depth += 1;
        if self.depth > self.max_depth {
            return Err("Maximum nesting depth exceeded".to_string());
        }
        
        let mut object = serde_json::Map::new();
        self.advance(); // consume '{'
        
        // Skip any leading commas
        while self.current_token == Token::Comma {
            self.advance();
        }
        
        while self.current_token != Token::RightBrace && self.current_token != Token::EOF {
            // Parse key
            let key = match &self.current_token {
                Token::String(s) => {
                    let k = s.clone();
                    self.advance();
                    k
                }
                Token::RightBrace => break,
                Token::Comma => {
                    self.advance();
                    continue;
                }
                _ => {
                    // Try to recover by treating current token as a string key
                    let k = format!("{:?}", self.current_token);
                    self.advance();
                    k
                }
            };
            
            // Expect colon
            if self.current_token == Token::Colon {
                self.advance();
            } else if self.current_token != Token::EOF && self.current_token != Token::RightBrace {
                // Missing colon, but continue anyway
            }
            
            // Parse value
            let value = self.parse_value()?;
            object.insert(key, value);
            
            // Handle comma
            if self.current_token == Token::Comma {
                self.advance();
                // Skip multiple commas
                while self.current_token == Token::Comma {
                    self.advance();
                }
            } else if self.current_token != Token::RightBrace && self.current_token != Token::EOF {
                // Missing comma, but continue if not at end
            }
        }
        
        // Consume closing brace if present
        if self.current_token == Token::RightBrace {
            self.advance();
        }
        
        self.depth -= 1;
        Ok(serde_json::Value::Object(object))
    }
    
    fn parse_array(&mut self) -> Result<serde_json::Value, String> {
        self.depth += 1;
        if self.depth > self.max_depth {
            return Err("Maximum nesting depth exceeded".to_string());
        }
        
        let mut array = Vec::new();
        self.advance(); // consume '['
        
        // Skip any leading commas
        while self.current_token == Token::Comma {
            self.advance();
        }
        
        while self.current_token != Token::RightBracket && self.current_token != Token::EOF {
            if self.current_token == Token::Comma {
                self.advance();
                continue;
            }
            
            let value = self.parse_value()?;
            array.push(value);
            
            // Handle comma
            if self.current_token == Token::Comma {
                self.advance();
                // Skip multiple commas
                while self.current_token == Token::Comma {
                    self.advance();
                }
            } else if self.current_token != Token::RightBracket && self.current_token != Token::EOF {
                // Missing comma, but continue if not at end
            }
        }
        
        // Consume closing bracket if present
        if self.current_token == Token::RightBracket {
            self.advance();
        }
        
        self.depth -= 1;
        Ok(serde_json::Value::Array(array))
    }
}

fn escape_string_for_json(s: &str, ensure_ascii: bool) -> String {
    let mut result = String::new();
    
    for ch in s.chars() {
        match ch {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            '\u{0008}' => result.push_str("\\b"),
            '\u{000C}' => result.push_str("\\f"),
            c if ensure_ascii && !c.is_ascii() => {
                // Escape non-ASCII characters
                for unit in c.encode_utf16(&mut [0; 2]) {
                    result.push_str(&format!("\\u{:04x}", unit));
                }
            }
            c if c.is_control() => {
                // Escape other control characters
                result.push_str(&format!("\\u{:04x}", c as u32));
            }
            c => result.push(c),
        }
    }
    
    result
}

fn format_json_value(value: &serde_json::Value, ensure_ascii: bool, indent: usize, current_indent: usize) -> String {
    match value {
        serde_json::Value::Null => "null".to_string(),
        serde_json::Value::Bool(b) => b.to_string(),
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::String(s) => {
            format!("\"{}\"", escape_string_for_json(s, ensure_ascii))
        }
        serde_json::Value::Array(arr) => {
            if arr.is_empty() {
                "[]".to_string()
            } else if indent > 0 {
                let mut result = "[\n".to_string();
                let inner_indent = current_indent + indent;
                for (i, item) in arr.iter().enumerate() {
                    result.push_str(&" ".repeat(inner_indent));
                    result.push_str(&format_json_value(item, ensure_ascii, indent, inner_indent));
                    if i < arr.len() - 1 {
                        result.push(',');
                    }
                    result.push('\n');
                }
                result.push_str(&" ".repeat(current_indent));
                result.push(']');
                result
            } else {
                let items: Vec<String> = arr.iter()
                    .map(|v| format_json_value(v, ensure_ascii, 0, 0))
                    .collect();
                format!("[{}]", items.join(","))
            }
        }
        serde_json::Value::Object(obj) => {
            if obj.is_empty() {
                "{}".to_string()
            } else if indent > 0 {
                let mut result = "{\n".to_string();
                let inner_indent = current_indent + indent;
                let mut items: Vec<_> = obj.iter().collect();
                items.sort_by_key(|(k, _)| k.as_str());
                
                for (i, (key, value)) in items.iter().enumerate() {
                    result.push_str(&" ".repeat(inner_indent));
                    result.push_str(&format!("\"{}\"", escape_string_for_json(key, ensure_ascii)));
                    result.push_str(": ");
                    result.push_str(&format_json_value(value, ensure_ascii, indent, inner_indent));
                    if i < items.len() - 1 {
                        result.push(',');
                    }
                    result.push('\n');
                }
                result.push_str(&" ".repeat(current_indent));
                result.push('}');
                result
            } else {
                let mut items: Vec<_> = obj.iter().collect();
                items.sort_by_key(|(k, _)| k.as_str());
                let pairs: Vec<String> = items.iter()
                    .map(|(k, v)| format!("\"{}\":{}", 
                        escape_string_for_json(k, ensure_ascii),
                        format_json_value(v, ensure_ascii, 0, 0)))
                    .collect();
                format!("{{{}}}", pairs.join(","))
            }
        }
    }
}

#[pyfunction]
fn _repair_json_rust(json_string: &str, ensure_ascii: bool, indent: usize) -> PyResult<String> {
    // Try to parse and repair the JSON
    let mut parser = Parser::new(json_string);
    
    match parser.parse() {
        Ok(value) => {
            // Format the repaired JSON
            let formatted = format_json_value(&value, ensure_ascii, indent, 0);
            Ok(formatted)
        }
        Err(_) => {
            // If parsing completely fails, return null
            Ok("null".to_string())
        }
    }
}

#[pymodule]
fn _fast_json_repair(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(_repair_json_rust, m)?)?;
    Ok(())
}

